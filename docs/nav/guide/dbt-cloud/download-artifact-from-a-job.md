# Download the latest artifacts from a Job

Better than looking at the Run ID which is not static all the time, we're able to implicitly tell `dbterd` to retrieve the latest artifacts from a Job (latest run) by using the [Retrieve Job Artifact](https://docs.getdbt.com/dbt-cloud/api-v2#/operations/Retrieve%20Job%20Artifact) endpoint.

The _Prerequisites_ and _Steps_ will be pretty similar to [Download artifacts from a Job Run](./download-artifact-from-a-job-run.md), mostly everything is the same but we will specify **JOB ID** instead of the _JOB RUN ID_.

!!! NOTE
    _JOB RUN ID_ takes precedence to _JOB ID_ if specified

Our dbt Cloud's Job will have the URL constructed as:

```log
https://<host_url>/deploy/<account_id>/projects/irrelevant/jobs/<job_id>
```

In the above:

| URL Part          | Environment Variable            | CLI Option                | Description                                                               |
|-------------------|---------------------------------|---------------------------|---------------------------------------------------------------------------|
| `job_id`          | `DBTERD_DBT_CLOUD_JOB_ID` | `--dbt-cloud-job-id` | dbt Cloud job ID |

- Fill `your_value` and set the environment variable as below:

```bash
export DBTERD_DBT_CLOUD_SERVICE_TOKEN=your_value
export DBTERD_DBT_CLOUD_ACCOUNT_ID=your_value
export DBTERD_DBT_CLOUD_JOB_ID=your_value
export DBTERD_DBT_CLOUD_HOST_URL=your_value # optional, default = cloud.getdbt.com
export DBTERD_DBT_CLOUD_API_VERSION=your_value # optional, default = v2
```

- Generate ERD:

```bash
dbterd run --dbt-cloud [-s <dbterd selection>]
```

And the sample logs:

```log
dbterd - INFO - Run with dbterd==1.0.0 (main.py:54)
dbterd - INFO - Using dbt project dir at: C:\Sources\dbterd (executor.py:46)
dbterd - INFO - Downloading...[URL: https://hidden/api/v2/accounts/hidden/jobs/hidden/artifacts/manifest.json] (administrative.py:68)
dbterd - INFO - Completed [status: 200] (administrative.py:71)
dbterd - INFO - Downloading...[URL: https://hidden/api/v2/accounts/hidden/jobs/hidden/artifacts/catalog.json] (administrative.py:68)
dbterd - INFO - Completed [status: 200] (administrative.py:71)
dbterd - INFO - Using dbt artifact dir at: hidden (executor.py:73)
dbterd - INFO - Collected 4 table(s) and 3 relationship(s) (test_relationship.py:59)
dbterd - INFO - C:\Sources\dbterd\target/output.dbml (executor.py:170)
```
