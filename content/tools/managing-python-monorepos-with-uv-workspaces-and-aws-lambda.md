Title: Managing Python Monorepos with uv Workspaces and AWS Lambda
Date: 2026-01-19
Modified: 2026-01-19
Category: Tools
Tags: python, uv, tooling, aws, lambda

uv workspaces are a super tool when developing interconnected Python packages, especially in mono-repo setups. uv will set it up pretty automatically if you have a `pyproject.toml` at the root of the repo and you run `uv init` inside a subfolder.

What this means is:
 - only **one** venv will be set up, with all dependencies for all projects (this is pretty nice for the IDE because you don't need to keep switching venvs, but note the important caveat below)
 - you can reference a local project by adding it in `[tool.uv.sources]`, and uv will automatically install it as editable (so you won't need to build each time you make a change and keep reinstalling your project):

```toml
[tool.uv.sources]
common_logging = { workspace = true }
```

* one caveat: if your projects have conflicting dependencies, uv will fail the install! For microservices, it is probably best to keep dependencies on compatible versions anyway
* another caveat: since there is only one venv, it's possible the IDE will detect a package that is not really in the project dependencies, and you accidentally import it! This can easily go unnoticed during local development.
* for that, you might be better off forgoing workspaces and using a path dependency:

```toml
[tool.uv.sources]
common_logging = {
	path = "../common/logging", editable = true
}
```

I have decided to keep using uv workspaces, but we have a CI check to catch that type of problem before it reaches production.

## Running uv in a workspace

From the root of a workspace, `uv sync` will install **only** the workspace-level packages.  Likewise `uv run` will not install all the packages.  This is **not** a way to specify common dependencies, because they will only be installed if the workspace root is installed (so for example `uv export` inside of the package will not include those "shared" deps).

Now, as you go into a package and run `uv sync`, uv will add the dependencies from that package to the venv... so eventually you will have everything installed.  But you can't be sure that is always the case.  This is also nice if you want to install deps for only one package, before running tests in CI, to make sure it does not accidentally depend on the other packages' dependencies.

To run and include all package dependencies (needed for example for a type checker!), use

```
uv run --all-packages
```

## Use in Docker build

The following examples assume **AWS Lambda container images**, which explains some of the paths (`/var/task`, `/var/lang/lib`) and the base images used. The general approach still applies to non-Lambda containers, but paths and base images would need to be adjusted.

There are two catches:

* you don't want to install all the workspace dependencies necessarily — some are not shared among all your microservices
* you don't want to install the local dependencies in the same layer as the core dependencies, because the core dependencies are less likely to change (and, more importantly, are much bigger)

This is especially important for Lambda images, where image size and layer caching directly impact cold start performance.

I struggled a bit with the latter, but in fact uv makes it rather easy. It's not super well documented though — there are many different ways to get there that will sort of work but leave you with some cruft in the final image.

### First attempt using uv sync

* you do need to copy all the `pyproject.toml` files and the single `uv.lock` file that you are going to need. This includes all your local dependencies, and that makes sense — if you changed a requirement in a local dependency, it's now part of your core deps, and you can include it in the base layer

```docker
COPY pyproject.toml uv.lock /build
COPY services/common/logging/pyproject.toml /build/services/common/logging/
COPY services/${SERVICE_NAME}/pyproject.toml ./
```

* then, install the core deps, making sure you specify the `--package` argument to install only for that part of the workspace, and the `--no-install-local` argument to prevent including other workspace members:

```docker
RUN uv sync --frozen --no-install-local --no-dev --package ${SERVICE_NAME}
```

* next, the local dependencies… uv will figure out which ones of those are needed for the project based on the workspace graph:

```docker
COPY services/common /build/services/common
RUN uv sync --frozen --no-editable --no-install-project --no-dev --package ${SERVICE_NAME}
```

* and finally, the code for this service:

```docker
COPY services/${SERVICE_NAME} ./
RUN uv sync --frozen --no-editable --no-dev --package ${SERVICE_NAME}
```

I refined this a little bit, because the above will leave two copies of the source code (one under `/build/services` and one under the venv), which is undesirable in a Lambda image where size matters:

```docker
# Copy dependency files: workspace, and service project
COPY pyproject.toml uv.lock /build
COPY services/${SERVICE_NAME}/pyproject.toml ./

# Install core dependencies
RUN uv sync --frozen --no-install-local --no-dev --package ${SERVICE_NAME}
ENV PYTHONPATH=/build/.venv/lib/python3.14/site-packages

# Install local dependencies
RUN --mount=type=bind,source=services/common,target=/build/services/common \
    uv sync --frozen --no-editable --no-install-project --no-dev --package ${SERVICE_NAME}

# Finally, copy the project source
COPY services/${SERVICE_NAME}/src /var/task
```

Now, the downside is that you are left with a few unneeded things in this final image: there are some leftovers from the venv and the uv command itself. I was also worried that running the uv command directly in the final image could leave me with some surprises, especially in a production Lambda environment.

### Second attempt using pip

To work around the above problem, I install the dependencies in two steps into separate folders. Then, I do another stage in the Docker build to collect all these dependencies into a clean final image.

Despite the title, this still relies on uv for dependency resolution — pip is only used for the final installation step, which keeps the runtime image simpler.

```docker
# --- Build Stage ---
FROM public.ecr.aws/lambda/python:3.14-arm64 AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ARG SERVICE_NAME

# Set up the working directory
WORKDIR /build

# Copy dependency files: workspace, and service project
COPY pyproject.toml uv.lock /build
COPY services/${SERVICE_NAME}/pyproject.toml /build/services/${SERVICE_NAME}/pyproject.toml

# Install core dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-local --no-dev --package ${SERVICE_NAME}

# Install common dependencies
RUN uv export --package ${SERVICE_NAME} --no-editable --no-dev --frozen --format requirements.txt | \
    grep '^./services/common' > common.txt
RUN --mount=type=bind,source=services/common,target=/build/services/common \
    uv pip install --no-deps -r common.txt --target /build/common

# Application code (we could use uv pip install here too, but this is simpler)
COPY services/${SERVICE_NAME}/src /build/app

FROM public.ecr.aws/lambda/python:3.14-arm64 AS final

# Copy core dependencies from venv
COPY --from=builder /build/.venv/lib /var/lang/lib

# Copy common
COPY --from=builder /build/common /var/task

# Application code
COPY --from=builder /build/app /var/task

# Set the CMD to your handler
CMD [ "ingestion_worker.main.handler" ]
```

This results in a smaller, cleaner final image that contains only what Lambda needs at runtime.
