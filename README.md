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