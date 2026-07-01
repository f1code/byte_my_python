Title: GitHub PR Review "View Deployment" button, with Dokku
Date: 2026-07-01
Modified: 2026-07-01
Category: Tools
Tags: dokku, review-apps, github-actions, deployment

I have been playing with review apps linked directly from GitHub PRs. The goal is simple: when someone opens a pull request, GitHub should show a link to a running preview of that branch.

I use Dokku for deployment of the app on the VPS and it works fine for the purpose of creating the one-shot, PR review
application.  It's all driven through CLI so very scriptable to fit into a GitHub Action workflow.
I ran into a few snags I should document.

## Give each PR a URL

The first thing to set up is wildcard DNS. I want each PR review app to get a predictable hostname, something like:

```text
pr-123.example.com
```

Once the wildcard points at the Dokku host, the workflow can set the app’s domain during deployment:

```bash
dokku domains:set "${APP_NAME}" "${APP_HOSTNAME}"
```

Then Let’s Encrypt can issue the certificate for that review app:

```bash
dokku letsencrypt:set "${APP_NAME}" email "${LETSENCRYPT_EMAIL}"
dokku letsencrypt:enable "${APP_NAME}"
```

Nothing especially magical here, but it is nice that this is just Dokku commands. The PR gets a real HTTPS URL without provisioning a separate load balancer, ingress controller, or whatever other bit of cloud ceremony usually comes with “temporary app with HTTPS”.

## Storage

If the app needs persistent files, create named storage for that PR’s review app and mount it into the container:

```bash
dokku storage:create "data-${APP_NAME}"
dokku storage:mount "${APP_NAME}" "data-${APP_NAME}" --container-dir /data
```

That gives the app a stable `/data` directory for the lifetime of the review app. It is still disposable, just not “lose every uploaded file on the first restart” disposable.

I also used another trick to initialize the storage from production.  This gives me 2 things:

 - make sure the database migrations are going to work correctly on production data
 - make the production data available during review

In my case it was simple... in some cases there are references to external systems in the production data and
things are not quite that easy.

```bash
TARGET=`dokku storage:info data-$APP_NAME --format json | jq -r .host_path`
sqlite3 /data/production/production.db ".backup ${TARGET}/${APP_NAME}.db"
```

(just before the `dokku storage:mount` command)

You might also use `pg_dump` to take a postgres backup, or `rsync` to just sync directory content.

## Linking from the PR

The important part is on the GitHub side: expose the review app as an environment URL. That way GitHub puts the link right on the PR instead of making everyone dig through CI logs.

The workflow shape is roughly:

```yaml
  deploy-review-app:
    name: Build, push, and deploy review app
    runs-on: ubuntu-latest
    environment:
      name: pr-${{ github.event.number }}
      url: ${{ steps.review_app_url.outputs.review_app_url }}
```

This will create an environment using the PR number, and associate an URL based on a step output
(`review_app_url`).  I created a step just for the output:

```yaml
      - name: Generate review app URL
        id: review_app_url
        run: |
          # Pass the URL to the environment URL via step outputs
          APP_NAME="gradebee-pr-${{ github.event.number }}"
          echo "review_app_url=https://$APP_NAME.test.gradebee.app" >> $GITHUB_OUTPUT
```

One gotcha: GitHub secret masking can prevent the URL from showing up.

If the environment URL matches a secret value, GitHub may redact it and refuse to display it. So if the domain is stored as a secret, and the final URL contains that exact domain, the PR link can mysteriously disappear. In this case, the domain name itself is not really a secret, so it is better as a variable or plain configuration value. Keep the actual credentials in secrets; do not make the public hostname one.

One other thing: in my case I was fine with re-using the production secret for the review app (it has to do with user
authentication, and I wanted to have the same users on both sides).  But if you need to differentiate, you'll have to do
a layered approach:

 - use a `live` environment with production secret
 - put the test secret at the repository level

This way when the production deployment runs it uses the `live` secrets, and the test deployments (which have a blank,
just-created environment) will fall back to the repo secrets.

## Cleanup

The other half of PR review apps is making sure they actually go away.

On the GitHub side, delete the temporary environment when the PR closes:

```yaml
  - name: Clean up Github environment
    env:
      GH_TOKEN: ${{ secrets.ENV_ADMIN_TOKEN }}
    run: |
      gh api \
        --method DELETE \
        -H "Accept: application/vnd.github+json" \
        /repos/${{ github.repository }}/environments/pr-${{ github.event.number }} || true
```

For this to work you need to generate, and store in a secret `ENV_ADMIN_TOKEN`, a fine-grained "Personal Access Token"
with read-write access to administration of the repository ([doc link](https://docs.github.com/en/rest/deployments/environments?apiVersion=2026-03-10#delete-an-environment)).  The regular `GITHUB_TOKEN` is not enough.

On the Dokku side, destroy the app and its storage:

```bash
dokku apps:destroy "${APP_NAME}"
dokku storage:destroy "data-${APP_NAME}"
```

The storage cleanup is easy to forget, especially if the app itself disappears cleanly. But if every PR creates a named volume, those leftovers add up.

## Takeaway

This is the kind of setup I like: a few boring shell commands glued into CI, rather than a bespoke review-app platform. GitHub already has a place to show the PR link, and Dokku has enough primitives to stand up the preview behind it.

The main thing is to be deliberate about what is disposable: app, domain, GitHub environment, storage. If you create all four on PR open/update, clean up all four on close. Otherwise your “temporary” review apps become a very quiet little infrastructure archaeology project.

Existing, public github projects can be a good source of inspiration, and the whole workflow as described above can be
viewed on the [GradeBee repository](https://github.com/f1code/GradeBee).
