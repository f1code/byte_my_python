Title: Testing Lambda Functions with LocalStack and pytest
Date: 2026-01-25
Modified: 2026-01-25
Category: Tools
Tags: python, testing, pytest, aws, lambda, localstack

When integration-testing code that calls AWS Lambda, you don't always want to hit the real thing. LocalStack gives you a local, containerized version of AWS services — including Lambda — that you can spin up, use, and tear down as part of your test suite.

Here's a pattern I've been using: create a Lambda function on the fly inside a pytest fixture, wait for it to become active, then hand off a boto3 client to the tests. Sounds straightforward, but there are a few gotchas.

## The fixture

```python
@pytest.fixture(scope="module")
def update_schema_lambda(testdata_dir: Path, config: Config) -> Generator[LambdaClient, None, None]:
    with (
        LocalStackContainer()
        .with_services("lambda")
        .with_volume_mapping(str(testdata_dir), "/testdata")
        .with_volume_mapping("/var/run/docker.sock", "/var/run/docker.sock")
    ) as container:
        endpoint_url = container.get_url()

        result = container.exec(
            """sh -c 'cd /testdata && zip /tmp/lambda.zip mock_update_schema.py'"""
        )
        assert result.exit_code == 0
        result = container.exec(f"""
        awslocal lambda create-function \
    --function-name {config.update_metadata_function} \
    --region us-east-1 \
    --runtime python3.9 \
    --handler mock_update_schema.handler \
    --memory-size 128 \
    --zip-file fileb:///tmp/lambda.zip \
    --role arn:aws:iam::000000000000:role/lambda-role
                       """)
        assert result.exit_code == 0
        result = container.exec(f"""
        awslocal lambda wait function-active-v2 \
    --region us-east-1 \
    --function-name {config.update_metadata_function}
    """)
        assert result.exit_code == 0
        client = boto3.client("lambda", endpoint_url=endpoint_url)
        yield client
```

Let's break it down.

## Starting the container

The `LocalStackContainer` (from testcontainers) spins up LocalStack with only the services you need. Here we're mounting two volumes:

- `/testdata` — where the Lambda handler code lives
- `/var/run/docker.sock` — LocalStack needs this to run Lambdas in their own containers (Lambda-in-Docker)

## Creating the Lambda

Inside the container, we use `awslocal` (LocalStack's wrapper around the AWS CLI) to zip up the handler and create the function. Nothing too surprising here, except for one thing: **always pass `--region`**.

LocalStack can be picky about regions. If you omit `--region`, it might default to something unexpected, and then your boto3 client (which defaults to `us-east-1`) won't find your function. Save yourself the debugging headache and be explicit.

## Waiting for the Lambda to be ready

This is the part that bit me:

```bash
awslocal lambda wait function-active-v2 \
    --region us-east-1 \
    --function-name {config.update_metadata_function}
```

Lambda functions aren't invocable immediately after creation. The `wait function-active-v2` command blocks until the function transitions to the `Active` state. Skip this, and your first invoke will likely fail with a cryptic error about the function not being ready.

## Getting the endpoint URL

Once the container is up, `container.get_url()` gives you the endpoint URL to pass to boto3:

```python
client = boto3.client("lambda", endpoint_url=endpoint_url)
```

This tells boto3 to talk to LocalStack instead of real AWS. Without it, your tests would try to hit production (and probably fail with auth errors, or worse, succeed and cost you money).

## Putting it together

With this fixture, any test that depends on `update_schema_lambda` gets a fully-configured boto3 Lambda client pointing at a fresh, ephemeral LocalStack instance with the mock function already deployed and ready to invoke.

The container tears down automatically when the module's tests finish, thanks to the context manager.

One last tip: if your tests are slow, consider `scope="session"` instead of `scope="module"` — but be aware that tests will then share state, so make sure your Lambda is idempotent or reset between tests.
