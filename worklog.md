\# Project Worklog — CustomerLabs Attribution Assessment



\## Project Overview



This project implements a marketing attribution pipeline using the public Google Analytics 4 (GA4) sample dataset in BigQuery. The goal is to compare First-Click and Last-Click attribution for purchase conversions, validate the data with dbt tests, demonstrate event ingestion, and present the results in a Streamlit dashboard.



The work was developed incrementally, with the models, Python scripts, dashboard, and documentation maintained in Git.



\## Development Log



\### Entry 1 — Project setup and environment



Set up the local project workspace on Windows and created a Python virtual environment to keep the project's dependencies separate from the system environment. Prepared the dbt project and configured it to use BigQuery as the data warehouse.



The GCP project and BigQuery dataset used for development are `storied-precept-511013-d2` and `labsattribution\_dbt`, respectively.



\### Entry 2 — BigQuery connection and dbt configuration



Configured the dbt BigQuery adapter and verified that the project could connect to BigQuery using the available Google authentication. Organized the SQL models into staging, intermediate, and marts layers to keep raw-data preparation separate from business logic.



Staging and intermediate models are configured as views, while the mart models are materialized as tables.



\### Entry 3 — GA4 staging model



Created `stg\_ga4\_events.sql` to provide a standardized starting point for downstream transformations. The purpose of this layer is to make the source event data easier to work with and to keep source-specific handling out of the attribution logic.



\### Entry 4 — Conversion and marketing touchpoint models



Developed intermediate models to identify purchase conversions and marketing touchpoints.



The main models include:



\- `int\_purchase\_conversions.sql` — prepares purchase conversion records.

\- `int\_marketing\_touchpoints.sql` — prepares eligible marketing interaction records.

\- `int\_attribution\_touches.sql` — supports the matching of conversions with their eligible touchpoints.



Separating these transformations makes the attribution logic easier to inspect, test, and maintain.



\### Entry 5 — First-Click and Last-Click attribution



Implemented First-Click and Last-Click attribution in separate mart models and combined their results in `mart\_attribution.sql`.



The attribution logic uses a 14-day lookback window. First-Click assigns the earliest eligible touchpoint within that window, while Last-Click assigns the latest eligible touchpoint. Conversions without an eligible touchpoint remain unattributed rather than being assigned an arbitrary source.



During validation, I reviewed the purchase-to-attribution matching logic and removed `transaction\_id` from the join conditions where it was not appropriate for matching the prepared records. The matching uses the user identifier and purchase timestamp.



\### Entry 6 — dbt tests and data validation



Added data quality tests for required fields in the purchase conversion and attribution models.



Ran the dbt test command:



`dbt test --project-dir attribution\_dbt`



The configured tests passed. They check that the conversion timestamp and user identifier in the purchase model, and the purchase timestamp and user identifier in the attribution mart, are not null.



The attribution mart contained 5,692 conversion records in the validated run. First-Click attributed 5,400 records, and Last-Click attributed 5,400 records. The remaining 292 records had no eligible touchpoint under the configured attribution rules and lookback window.



These figures describe the validated dataset at that point in development.



\### Entry 7 — Event ingestion demonstration



Created Python scripts under `scripts/` to demonstrate inserting a small set of sample events into a separate BigQuery table named `streaming\_demo\_events`.



The demonstration uses five sample events and includes event identifiers, user identifiers, event names, timestamps, source, medium, campaign, and an optional event value. A verification script queries the table to confirm that the loaded events are visible.



The initial attempt to use BigQuery streaming inserts was rejected because streaming inserts were not available in the current free-tier environment. I changed the demonstration to use a BigQuery batch-load job instead and documented this limitation.



The script checks existing event identifiers before loading new events. This is a basic safeguard against repeated runs, not a guarantee of exactly-once delivery under concurrent runs or every possible failure scenario.



\### Entry 8 — Streamlit dashboard



Created `scripts/dashboard.py` to present the attribution results through a browser-based dashboard.



The dashboard includes:



\- Total conversion count.

\- First-Click and Last-Click attributed conversion totals.

\- A comparison chart showing attributed and unattributed conversions.

\- A trend chart covering the latest 14-day period represented in the available data.

\- A breakdown of First-Click conversions by source.

\- A table showing the demo events loaded into BigQuery.

\- A refresh control for rerunning the dashboard queries.



During development, I corrected the timestamp handling in the trend query. The mart's `purchase\_timestamp` column is stored as an integer representing microseconds, so the query converts it with `TIMESTAMP\_MICROS()` before extracting the date.



I verified that the dashboard could query BigQuery and display the conversion totals, source breakdown, trend, and demo events.



\### Entry 9 — Documentation and Git version control



Updated the README to explain the project structure, attribution assumptions, dbt execution commands, event ingestion demonstration, and dashboard launch instructions.



Committed and pushed the implementation incrementally to the GitHub repository:



https://github.com/muthukrishnan760/Project-attribution-dbt



The dashboard and its run instructions were committed separately from the earlier model and ingestion work. This keeps the development history easier to follow.



\## Key Technical Decisions



\- \*\*Lookback window:\*\* Use a 14-day lookback for eligible marketing touchpoints.

\- \*\*First-Click:\*\* Select the earliest eligible touchpoint for a conversion.

\- \*\*Last-Click:\*\* Select the latest eligible touchpoint for a conversion.

\- \*\*Unattributed conversions:\*\* Preserve conversions that have no eligible touchpoint rather than assigning a source without evidence.

\- \*\*Data organization:\*\* Use staging, intermediate, and mart layers in dbt.

\- \*\*Validation:\*\* Use dbt data tests for important non-null fields.

\- \*\*Demo ingestion:\*\* Use batch loading because streaming inserts were unavailable in the current environment.

\- \*\*Event identifiers:\*\* Check existing identifiers before loading demo events, while recognizing that this is not a complete exactly-once processing solution.

\- \*\*Dashboard trend:\*\* Use the latest available conversion date in the dataset so historical sample data can still produce a meaningful trend.

\- \*\*Version control:\*\* Maintain the work in Git and push changes to GitHub as the implementation progresses.



\## Known Limitations and Further Improvements



The current event ingestion demonstration is batch-based and should not be described as a true real-time streaming pipeline. A production implementation could use a supported streaming ingestion service, with explicit handling for retries, deduplication, late-arriving events, and ingestion monitoring.



The event identifier check is suitable as a small demonstration but is not a substitute for a robust idempotency design. Concurrent execution and retries would need stronger safeguards.



The current dbt tests cover selected non-null requirements. Additional tests could check uniqueness, accepted values, attribution consistency, and referential integrity.



Identity resolution is limited by the identifiers available in the source data. Cross-device or cross-session identity resolution is not implemented.



The dashboard queries BigQuery directly and is intended for assessment demonstration rather than a production monitoring environment. Production use would require stronger error handling, query-cost controls, freshness indicators, and operational monitoring.



\## Current Project Status



\- dbt staging, intermediate, and mart models implemented.

\- First-Click and Last-Click attribution implemented.

\- Configured dbt tests passing in the validated run.

\- Five sample events loaded and verified in the BigQuery demo table.

\- Streamlit dashboard implemented and verified against BigQuery.

\- README updated with execution and dashboard instructions.

\- Code and documentation pushed to the GitHub repository.



\## Next Steps



\- Add a clear architecture diagram showing the data flow from GA4 through BigQuery and dbt to the dashboard.

\- Add design sketches explaining the attribution flow and dashboard layout.

\- Review the final README and runbook for reproducibility.

\- Prepare a short demonstration covering the models, tests, sample event ingestion, and dashboard.

\- Capture the final demonstration and submit the repository and demo links as required by the assessment.

