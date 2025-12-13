# Read the latest artifacts from an environment

This is a guideline on how to query the dbt cloud metadata given an environment by using [dbt Cloud Discovery API](https://docs.getdbt.com/docs/dbt-cloud-apis/discovery-api). It doesn't require `JOB ID` or `JOB RUN ID`, but rather the dbt Cloud's `ENVIRONMENT ID`. Especially, with this method, `dbterd` doesn't require downloading files beforehand anymore, the ERD will be generated on the fly 🚀.

`dbterd` now understands GraphQL connections which are exposed by dbt Cloud Discovery API endpoint:

```log
https://metadata.YOUR_ACCESS_URL/graphql
```

> Replace `{YOUR_ACCESS_URL}` with the appropriate [Access URL](https://docs.getdbt.com/docs/cloud/about-cloud/regions-ip-addresses) for your region and plan

!!! note "Prerequisites"
    - dbt Cloud [multi-tenant](https://docs.getdbt.com/docs/cloud/about-cloud/tenancy#multi-tenant) or [single tenant](https://docs.getdbt.com/docs/cloud/about-cloud/tenancy#single-tenant) account ☁️
    - You must be on a [Team or Enterprise plan](https://www.getdbt.com/pricing/) 💰
    - Your projects must be on dbt version 1.0 or later 🏃

The assumption is that you've already got the dbt Cloud project ready and have at least 1 environment, and 1 job run successfully in this environment.

## 1. Prepare the environment variables

As mentioned above, the API Endpoint will look like:

```log
https://metadata.YOUR_ACCESS_URL/graphql
```

For example, if your multi-tenant region is North America, your endpoint is `https://metadata.cloud.getdbt.com/graphql`. If your multi-tenant region is EMEA, your endpoint is `https://metadata.emea.dbt.com/graphql`.

And the dbt Cloud's Environment will have the URL constructed as:

```log
https://<host_url>/deploy/irrelevant/projects/irrelevant/environments/<environment_id>
```

In the above:

| URL Part          | Environment Variable            | CLI Option                | Description                                                               |
|-------------------|---------------------------------|---------------------------|---------------------------------------------------------------------------|
| `host_url`        | `DBTERD_DBT_CLOUD_HOST_URL` | `--dbt-cloud-host-url` | Host URL (also known as [Access URL](https://docs.getdbt.com/docs/cloud/about-cloud/regions-ip-addresses)) with prefix of `metadata.` |
| `environment_id`  | `DBTERD_DBT_CLOUD_ENVIRONMENT_ID` | `--dbt-cloud-environment-id` | dbt Cloud environment ID |

Besides, we need another one which is very important, the service token:

- Go to **Account settings** / **Service tokens**. Click _+ New token_
- Enter _Service token name_ e.g. "ST_dbterd_metadata"
- Click _Add_ and select `Metadata Only` permission. Optionally, select the right project or all by default
- Click _Save_
- Copy token & Pass it to the Environment Variable (`DBTERD_DBT_CLOUD_SERVICE_TOKEN`) or the CLI Option (`--dbt-cloud-service-token`)

Finally, fill in `your_value` and execute the (Linux or Macos) command below:

```bash
export DBTERD_DBT_CLOUD_HOST_URL=your_value e.g. metadata.cloud.getdbt.com
export DBTERD_DBT_CLOUD_SERVICE_TOKEN=your_value
export DBTERD_DBT_CLOUD_ENVIRONMENT_ID=your_value
```

Or in Powershell:

```bash
$env:DBTERD_DBT_CLOUD_HOST_URL="your_value"
$env:DBTERD_DBT_CLOUD_SERVICE_TOKEN="your_value"
$env:DBTERD_DBT_CLOUD_ENVIRONMENT_ID="your_value"
```

## 2. Generate ERD file

We're going to use a new command as `dbterd run-metadata` to tell `dbterd` to use dbt Cloud Discovery API with all above variables.

The command will look like:

```bash
dbterd run-metadata [-s <dbterd selection>]
```

> Behind the scenes, it will try to use the ERD GraphQL query built-in at [include/graphql_queries](https://github.com/datnguye/dbterd/tree/main/dbterd/include/graphql_queries)

and then, here is the sample console log:

```log
2024-02-03 19:57:57,514 - dbterd - INFO - Run with dbterd==1.0.0 (main.py:54)
2024-02-03 19:57:57,515 - dbterd - INFO - Looking for the query in: (hidden)/dbterd/include/graphql_queries/erd_query__test_relationship.gql (query.py:31)
2024-02-03 19:57:57,516 - dbterd - DEBUG - Getting erd data...[URL: https://metadata.cloud.getdbt.com/graphql/, VARS: {'environment_id': '(hidden)', 'model_first': 500, 'source_first': 500, 'exposure_first': 500, 'test_first': 500}] (graphql.py:40)
2024-02-03 19:57:58,865 - dbterd - DEBUG - Completed [status: 200] (graphql.py:48)
2024-02-03 19:57:58,868 - dbterd - INFO - Metadata result: 5 model(s), 2 source(s), 1 exposure(s), 21 test(s) (discovery.py:169)
2024-02-03 19:57:58,880 - dbterd - INFO - Collected 5 table(s) and 1 relationship(s) (test_relationship.py:44)
2024-02-03 19:57:58,881 - dbterd - INFO - (hidden)\target (executor.py:179)
```


Voila! Happy ERD _with dbt Cloud Metadata_ 🎉!
