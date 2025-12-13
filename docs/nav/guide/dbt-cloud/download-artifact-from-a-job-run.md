# Download artifacts from a Job Run

This is a guideline on how to download `manifest.json` and `catalog.json` from a Job Run by using [dbt CLoud Administrative API](https://docs.getdbt.com/docs/dbt-cloud-apis/admin-cloud-api), under the [Retrieve Run Artifact](https://docs.getdbt.com/dbt-cloud/api-v2#/operations/Retrieve%20Run%20Artifact) endpoint. Therefore, we don't need to run `dbt docs generate` locally anymore.

In order to support dbt Cloud users, `dbterd` is now having multiple CLI options starting with `--dbt-cloud` to let us configure the connection to the complete dbt Cloud Job Run.

!!! note "Prerequisites"
    - You have a dbt Cloud account with [Team and Enterprise plans](https://www.getdbt.com/pricing/) 💰
    - You have a job or go create a new job with a single step 🏃

        ```bash
        dbt docs generate
        ```
    - Make sure that you have at least 1 successful run ✅

## 1. Prepare the environment variables

Behind the scene, the API Endpoint will look like:

```log
https://{host_url}/api/{api_version}/accounts/{account_id}/runs/{run_id}/artifacts/{path}
```

And the dbt Cloud's Job Run will have the URL constructed as:

```log
https://<host_url>/deploy/<account_id>/projects/irrelevant/runs/<run_id>
```

In the above:

| URL Part          | Environment Variable            | CLI Option                | Description                                                               |
|-------------------|---------------------------------|---------------------------|---------------------------------------------------------------------------|
| `host_url`        | `DBTERD_DBT_CLOUD_HOST_URL` | `--dbt-cloud-host-url` | Host URL, also known as [Access URL](https://docs.getdbt.com/docs/cloud/about-cloud/regions-ip-addresses) (Default to `cloud.getdbt.com`) |
| `account_id`      | `DBTERD_DBT_CLOUD_ACCOUNT_ID` | `--dbt-cloud-account-id` | dbt Cloud Account ID |
| `run_id`          | `DBTERD_DBT_CLOUD_RUN_ID` | `--dbt-cloud-run-id` | dbt Cloud successful job run ID |
| `api_version`     | `DBTERD_DBT_CLOUD_API_VERSION` | `--dbt-cloud-api-version` | dbt Cloud API version (Default to `v2`) |
| `path`            | `N/A` | `N/A` | Artifact relative file path. You don't need to care about this part as `dbterd` managed it already |

Besides, we need another one which is very important, the service token:

- Go to **Account settings** / **Service tokens**. Click _+ New token_
- Enter _Service token name_ e.g. "ST_dbterd"
- Click _Add_ and select `Job Admin` permission. Optionally, select the right project or all by default
- Click _Save_
- Copy token & Pass it to the Environment Variable (`DBTERD_DBT_CLOUD_SERVICE_TOKEN`) or the CLI Option (`--dbt-cloud-service-token`)

Finally, fill in `your_value` and execute the (Linux or Macos) command below:

```bash
export DBTERD_DBT_CLOUD_SERVICE_TOKEN=your_value
export DBTERD_DBT_CLOUD_ACCOUNT_ID=your_value
export DBTERD_DBT_CLOUD_RUN_ID=your_value
export DBTERD_DBT_CLOUD_HOST_URL=your_value # optional, default = cloud.getdbt.com
export DBTERD_DBT_CLOUD_API_VERSION=your_value # optional, default = v2
```

Or in Powershell:

```powershell
$env:DBTERD_DBT_CLOUD_SERVICE_TOKEN="your_value"
$env:DBTERD_DBT_CLOUD_ACCOUNT_ID="your_value"
$env:DBTERD_DBT_CLOUD_RUN_ID="your_value"
$env:DBTERD_DBT_CLOUD_HOST_URL="your_value" # optional, default = cloud.getdbt.com
$env:DBTERD_DBT_CLOUD_API_VERSION="your_value" # optional, default = v2
```

## 2. Generate ERD file

We're going to use `--dbt-cloud` option to tell `dbterd` to use dbt Cloud API with all above variables.

The command will look like:

```bash
dbterd run --dbt-cloud [-s <dbterd selection>]
```

!!! NOTE
    You can not use `--dbt` option together with `--dbt-cloud`

and then, here is the sample console log:

```log
dbterd - INFO - Run with dbterd==1.0.0 (main.py:54)
dbterd - INFO - Using dbt project dir at: C:\Sources\dbterd (executor.py:46)
dbterd - INFO - Downloading...[URL: https://hidden/api/v2/accounts/hidden/runs/hidden/artifacts/manifest.json] (administrative.py:68)
dbterd - INFO - Completed [status: 200] (administrative.py:71)
dbterd - INFO - Downloading...[URL: https://hidden/api/v2/accounts/hidden/runs/hidden/artifacts/catalog.json] (administrative.py:68)
dbterd - INFO - Completed [status: 200] (administrative.py:71)
dbterd - INFO - Using dbt artifact dir at: hidden (executor.py:73)
dbterd - INFO - Collected 4 table(s) and 3 relationship(s) (test_relationship.py:59)
dbterd - INFO - C:\Sources\dbterd\target/output.dbml (executor.py:170)
```

Voila! Happy ERD 🎉!
