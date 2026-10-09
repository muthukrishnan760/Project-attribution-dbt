# Real-Time Attribution Dashboard

**CustomerLabs Data Engineer Assessment**

## Project Overview

This project looks at how different marketing channels contribute to website purchases. I am using GA4 event data, Google BigQuery, and dbt to prepare the data and calculate First-Click and Last-Click attribution.

The data models and attribution logic are the main focus at this stage. Event generation and the dashboard are planned for later, so they are not described as completed features.

## Tech Stack

- **Google BigQuery:** Stores the data and runs queries.
- **GA4 public dataset:** Provides the website event data.
- **dbt:** Transforms the raw events and builds the attribution models.
- **Git and GitHub:** Track code changes and manage the project repository.
- **Python and Streamlit:** Planned for event generation and the dashboard.

## Data Pipeline

The pipeline is organised into staging, intermediate, and mart models. Each layer handles a specific part of the process.

- **Staging:** Prepares GA4 event data for further use.
- **Purchase conversions:** Identifies purchase events and keeps details such as the user ID, purchase time, transaction ID, and revenue.
- **Marketing touchpoints:** Prepares traffic source, medium, campaign, and channel information.
- **Attribution touches:** Matches purchases with eligible earlier touchpoints from the same user within a 14-day lookback window.
- **Attribution mart:** Combines the First-Click and Last-Click results into a final table for analysis.

## Attribution Logic

The project currently uses two attribution models.

- **First-Click:** Gives credit to the earliest eligible touchpoint before a purchase.
- **Last-Click:** Gives credit to the latest eligible touchpoint before a purchase.

Both models use a 14-day lookback window. Purchases without an eligible touchpoint remain unattributed rather than being assigned a channel without supporting data.

## Current Progress

The following work has been completed:

- Set up dbt to work with BigQuery.
- Created staging, intermediate, and mart models.
- Implemented First-Click and Last-Click attribution logic.
- Built the final attribution table in BigQuery.
- Added data-quality tests for important fields and confirmed that all four tests pass.

## Current Results

The latest run of the attribution table produced these results:

| Metric | Count |
|---|---:|
| Total purchase records | 5,692 |
| First-Click attributed | 5,400 |
| Last-Click attributed | 5,400 |
| Unattributed purchases | 292 |

The remaining 292 purchases had no eligible touchpoints within the 14-day lookback window in the checks performed. They remain unattributed because there is no eligible touchpoint to support assigning a channel.

## Running the Project

Before running the commands, make sure your Python virtual environment is active and your dbt profile is configured to connect to BigQuery.

To build the final attribution model, run:

    dbt run --project-dir attribution_dbt --select mart_attribution

To run the data-quality tests, run:

    dbt test --project-dir attribution_dbt

## Output

The final table is available in BigQuery as:

`labsattribution_dbt.mart_attribution`

It contains purchase details and the corresponding First-Click and Last-Click attribution results.

## Next Steps

- Add tests for attribution logic and edge cases.
- Review purchases with missing transaction IDs and repeated purchase events.
- Develop Python-based event generation.
- Build a Streamlit dashboard to explore the attribution results.
- Improve the setup instructions so other people can run the project.

## Demo Event Ingestion

The Python demo in `scripts/stream_events.py` creates five sample marketing events and loads them into the BigQuery table `labsattribution_dbt.streaming_demo_events`. The script checks for existing demo event IDs before loading, and `scripts/verify_events.py` queries the table to verify the results.

### How to run

```powershell
python .\scripts\stream_events.py
python .\scripts\verify_events.py
```

### Free-tier limitation

BigQuery rejected streaming inserts in this project because streaming inserts are not allowed on the current free-tier setup. The demo therefore uses a BigQuery batch load job instead of true near-real-time streaming. This demonstrates event ingestion and verification, but it does not demonstrate streaming latency. The existing attribution models and tables are separate from this demo table.

### Idempotency note

The script skips event IDs already visible in the target table to avoid duplicate events on ordinary repeat runs. This is a simple demo safeguard, not a guarantee against concurrent runs or delayed query visibility. A production pipeline should use a durable deduplication strategy and monitor ingestion latency and failures.

## Dashboard

The project includes a Streamlit dashboard for exploring First-Click and Last-Click attribution results in BigQuery.

### Run the dashboard

From the project root, activate the virtual environment and run:

```powershell
.\.venv\Scripts\Activate.ps1
python -m streamlit run .\scripts\dashboard.py
```

Open the local URL shown in the terminal, usually `http://localhost:8501`.

### Dashboard features

- Total conversion count and First-Click vs Last-Click attribution comparison
- Conversion trend over the latest 14-day period available in the dataset
- First-Click conversions by source
- Demo event ingestion table showing batch-loaded events

**Note:** The demo event table uses BigQuery batch loading because streaming inserts are not available in the current free-tier environment. It is not a true real-time streaming feed.