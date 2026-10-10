# Marketing Attribution Pipeline and Dashboard

**CustomerLabs Data Engineer Assessment**

## 1. Project Overview

This project explores how different marketing touchpoints contribute to website purchases. I built a data pipeline using the public GA4 sample dataset, Google BigQuery, and dbt, with First-Click and Last-Click attribution models.

I also added a Python script to generate sample marketing events and load them into BigQuery, along with a Streamlit dashboard to explore the attribution results.

The event ingestion demo currently uses a BigQuery batch-load job because streaming inserts were not available in my current environment. I have documented that limitation rather than presenting the demo as a real-time streaming pipeline.

## 2. Tools Used

- **Google BigQuery:** Stores the source data, transformed models, and sample demo events.
- **GA4 public dataset:** Provides the website event data used for attribution.
- **dbt:** Organises the SQL transformations into staging, intermediate, and mart models.
- **Python:** Generates sample events and verifies the ingestion results.
- **Streamlit:** Displays the attribution results and sample events.
- **Git and GitHub:** Track the project changes and maintain the source code.

## 3. Architecture

The main pipeline follows this flow:

```text
GA4 Public Dataset
        |
        v
  Staging Model
        |
        v
 Intermediate Models
        |
        v
 First-Click and Last-Click Marts
        |
        v
  Combined Attribution Mart
        |
        v
  Streamlit Dashboard
```

The sample event demo follows a separate path:

```text
Python Event Generator
        |
        v
 BigQuery Batch-Load Job
        |
        v
 streaming_demo_events
        |
        v
 Verification Script / Dashboard
```

The sample events are not automatically included in the GA4 attribution calculations. The two paths demonstrate the transformation pipeline and the separate event-ingestion process.

More detail is available in [`docs/architecture.md`](docs/architecture.md) and [`docs/design-notes.md`](docs/design-notes.md).

## 4. Data Models

The dbt project is located in `attribution_dbt/`.

The main models are organised as follows:

| Model | Purpose |
|---|---|
| `stg_ga4_events` | Prepares GA4 event data for further transformations. |
| `int_purchase_conversions` | Identifies purchase events and prepares conversion details. |
| `int_marketing_touchpoints` | Prepares marketing touchpoint and traffic-source information. |
| `int_attribution_touches` | Matches purchases to eligible touchpoints. |
| `mart_first_click_attribution` | Produces First-Click attribution results. |
| `mart_last_click_attribution` | Produces Last-Click attribution results. |
| `mart_attribution` | Combines the attribution results for reporting. |

The models are built in BigQuery. The intermediate models keep the logic separated so it is easier to understand and troubleshoot.

## 5. Attribution Logic and Assumptions

I implemented two attribution models.

- **First-Click:** Assigns conversion credit to the earliest eligible marketing touchpoint before a purchase.
- **Last-Click:** Assigns conversion credit to the latest eligible marketing touchpoint before a purchase.

Both models use a 14-day lookback window.

Other assumptions and limitations:

- Purchases without an eligible touchpoint remain unattributed.
- Touchpoints and purchases are matched using the available GA4 pseudonymous user identifier.
- This matching does not resolve identities across different devices or browsers.
- Event timestamps determine touchpoint order. Events with identical timestamps may need a stable secondary key to guarantee deterministic ordering.
- Each model assigns full credit to its selected touchpoint. The models are separate reporting approaches, not fractional attribution models.

These are intentionally simple rules for comparing two commonly used attribution approaches.

## 6. Current Results and Tests

The latest validation run produced the following results:

| Metric | Count |
|---|---:|
| Total purchase conversions | 5,692 |
| First-Click attributed | 5,400 |
| Last-Click attributed | 5,400 |
| Unattributed purchases | 292 |

The 292 unattributed purchases did not have an eligible touchpoint within the configured lookback window in the checks performed.

I also ran the dbt data-quality tests. All four configured `not_null` tests passed for important conversion and attribution fields.

These results reflect the current dataset and model run. They may change if the underlying data or transformation logic changes.

## 7. Prerequisites

Before running the project, make sure you have:

- Python installed.
- Access to the configured Google Cloud project and BigQuery dataset.
- Google Cloud credentials that allow the required BigQuery operations.
- A working dbt profile configured for BigQuery.
- The project repository cloned locally.

The current setup uses the BigQuery project and dataset configured for this assessment. If you use a different Google Cloud project, update the dbt profile and relevant script configuration accordingly.

## 8. Running the dbt Pipeline

Run the following commands from the project root.

### Step 1: Activate the virtual environment

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If you have not created the environment yet, create one and install the dependencies specified by your project setup before continuing.

### Step 2: Check the dbt connection

```powershell
dbt debug --project-dir attribution_dbt
```

This checks the dbt configuration and connection. If it fails, review the active profile, project settings, credentials, and BigQuery permissions.

### Step 3: Build the attribution models

```powershell
dbt run --project-dir attribution_dbt
```

To run only the combined attribution mart:

```powershell
dbt run --project-dir attribution_dbt --select mart_attribution
```

Run the full project when you need to build or refresh the upstream models as well.

### Step 4: Run the tests

```powershell
dbt test --project-dir attribution_dbt
```

Review the command output and resolve any failed tests before relying on the results.

## 9. Running the Event Ingestion Demo

The event demo is implemented in `scripts/stream_events.py`. It generates five sample events and loads them into the BigQuery table `labsattribution_dbt.streaming_demo_events`.

Run:

```powershell
python .\scripts\stream_events.py
```

Then verify the loaded records:

```powershell
python .\scripts\verify_events.py
```

The verification script checks the target table for the demo events.

### Ingestion limitation

The script uses a BigQuery batch-load job, not a continuous streaming API. Streaming inserts were not available in the current free-tier environment, so this demo does not establish true streaming latency or continuous event processing.

The script checks for existing event IDs before loading. This helps avoid duplicates during ordinary repeat runs, but it does not guarantee exactly-once processing under concurrent execution or every possible retry scenario.

For production use, I would add a stronger event-ID-based deduplication process, safe retry handling, and monitoring for ingestion failures and event freshness.

## 10. Running the Dashboard

From the project root, activate the virtual environment and run:

```powershell
.\.venv\Scripts\Activate.ps1
python -m streamlit run .\scripts\dashboard.py
```

Open the local URL printed in the terminal, usually:

`http://localhost:8501`

The dashboard includes:

- Total purchase conversions.
- First-Click and Last-Click attribution comparison.
- A purchase trend for the latest available 14-day period in the dataset.
- A source-level attribution breakdown.
- A table of the sample events loaded into BigQuery.

The 14-day trend is based on the latest available dates in the dataset, not necessarily the current calendar date. The demo event panel reads from the separate batch-loaded event table.

## 11. Troubleshooting and Basic Checks

### dbt connection fails

Run:

```powershell
dbt debug --project-dir attribution_dbt
```

Check that the correct virtual environment is active, the BigQuery profile is configured, credentials are valid, and the account has the required permissions.

### dbt tests fail

Run:

```powershell
dbt test --project-dir attribution_dbt
```

Read the failing test output and inspect the relevant model and data. Do not assume the attribution results are valid until the failure is understood.

### Demo events are missing

Run the ingestion script again and inspect its output:

```powershell
python .\scripts\stream_events.py
```

Then check the table:

```powershell
python .\scripts\verify_events.py
```

If the events are still missing, check the configured Google Cloud project and dataset, BigQuery permissions, and the load-job error details.

### Dashboard does not start

Run:

```powershell
python -m streamlit run .\scripts\dashboard.py
```

Check the terminal output for missing dependencies, authentication problems, or BigQuery query errors. Confirm that the virtual environment is active and the configured credentials can access the required tables.

### Dashboard numbers look unexpected

Confirm that the dbt models have been built and that the dashboard is querying the intended BigQuery project and dataset. Remember that the sample event table is separate from the GA4 attribution models.

## 12. Cost and Performance Notes

The project uses BigQuery for transformations and reporting, so query execution and storage can incur costs depending on the account and billing configuration.

To keep usage under control:

- Select only the columns required by each model.
- Filter data to the relevant date range where possible.
- Avoid repeatedly rebuilding models when a smaller selection is sufficient.
- Review BigQuery job details if a query scans more data than expected.
- Monitor storage and query usage in the Google Cloud project.

Actual costs depend on the data processed, the selected BigQuery configuration, and the account's billing terms. This project does not claim a measured production cost.

## 13. Current Limitations and Next Improvements

The main parts of the project are implemented, but there are areas I would improve before using this as a production pipeline.

1. Replace the batch-load event demo with a streaming-capable ingestion path and measure ingestion latency.
2. Strengthen event deduplication and retry handling.
3. Add tests for attribution edge cases, including timestamp ties and repeated purchase events.
4. Improve monitoring for data freshness, ingestion failures, and dbt model failures.
5. Review the identity-matching assumptions and add a deterministic tie-breaker where appropriate.

I would prioritise reliable ingestion, clear attribution rules, and data-quality checks before adding more complex attribution models.

## 14. Repository Structure

The main project files are organised as follows:

```text
cuslabs-attri/
├── attribution_dbt/
│   └── models/
├── scripts/
│   ├── stream_events.py
│   ├── verify_events.py
│   └── dashboard.py
├── docs/
│   ├── architecture.md
│   └── design-notes.md
├── README.md
├── worklog.md
└── learning-notes.md
```

The dbt models, Python scripts, documentation, and worklog are kept separate so the project is easier to navigate.

## 15. Summary

This project brings together a dbt-based attribution pipeline, First-Click and Last-Click models, BigQuery validation, a Streamlit dashboard, and a small event-ingestion demo.

The attribution pipeline and dashboard are implemented. The event-ingestion demo currently uses batch loading rather than true streaming, and I have documented that limitation along with the areas that would need further work for a production deployment.