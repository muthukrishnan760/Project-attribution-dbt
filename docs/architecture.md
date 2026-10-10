\# CustomerLabs Attribution Pipeline — Architecture



\## 1. Overview



This project implements a marketing attribution pipeline using the public Google Analytics 4 (GA4) sample dataset in BigQuery. It transforms GA4 event data into purchase conversion records, identifies eligible marketing touchpoints, calculates First-Click and Last-Click attribution, and presents the results through a Streamlit dashboard.



A separate Python demonstration loads five sample marketing events into BigQuery using a batch-load job. This demonstrates event ingestion and verification, but it is not a real-time streaming implementation.



\## 2. Architecture Diagram



```mermaid

flowchart TD

&#x20;   A\["GA4 Public Sample Dataset<br/>BigQuery source events"]

&#x20;   B\["dbt Staging<br/>stg\_ga4\_events"]

&#x20;   C\["dbt Intermediate Models<br/>int\_purchase\_conversions<br/>int\_marketing\_touchpoints<br/>int\_attribution\_touches"]

&#x20;   D\["First-Click Attribution<br/>mart\_first\_click\_attribution"]

&#x20;   E\["Last-Click Attribution<br/>mart\_last\_click\_attribution"]

&#x20;   F\["Combined Attribution Mart<br/>mart\_attribution"]

&#x20;   G\["Streamlit Dashboard<br/>Conversion totals, comparison,<br/>trend and source breakdown"]



&#x20;   H\["Python Demo Scripts<br/>scripts/stream\_events.py"]

&#x20;   I\["BigQuery Batch-Load Job"]

&#x20;   J\["Demo Events Table<br/>streaming\_demo\_events"]

&#x20;   K\["Verification Script<br/>scripts/verify\_events.py"]



&#x20;   A --> B

&#x20;   B --> C

&#x20;   C --> D

&#x20;   C --> E

&#x20;   D --> F

&#x20;   E --> F

&#x20;   F --> G



&#x20;   H --> I

&#x20;   I --> J

&#x20;   J --> K

&#x20;   J --> G

```



\## 3. Tools and Technologies



| Component | Technology | Purpose |

|---|---|---|

| Source data | Public GA4 sample dataset | Supplies historical analytics events |

| Data warehouse | Google BigQuery | Stores source data, transformed models, attribution results, and demo events |

| Transformation | dbt Core with BigQuery adapter | Organizes SQL transformations into staging, intermediate, and mart layers |

| Data quality | dbt tests | Checks selected required fields for null values |

| Demo ingestion | Python and Google Cloud BigQuery client | Loads a small sample event batch into a separate table |

| Dashboard | Streamlit and pandas | Displays attribution metrics, source breakdowns, trends, and demo events |

| Version control | Git and GitHub | Tracks project changes and shares the implementation |



\## 4. BigQuery Project and Tables



\*\*Google Cloud project:\*\* `storied-precept-511013-d2`



\*\*Dataset:\*\* `labsattribution\_dbt`



\### dbt models



\- `stg\_ga4\_events` — standardizes the source event data.

\- `int\_purchase\_conversions` — prepares purchase conversion records.

\- `int\_marketing\_touchpoints` — prepares eligible marketing touchpoints.

\- `int\_attribution\_touches` — supports matching conversions to eligible touchpoints.

\- `mart\_first\_click\_attribution` — produces First-Click attribution.

\- `mart\_last\_click\_attribution` — produces Last-Click attribution.

\- `mart\_attribution` — combines conversion and attribution results for reporting.



Staging and intermediate models are configured as views, while mart models are materialized as tables.



\### Demo ingestion table



\- `streaming\_demo\_events` — stores the five sample events loaded by the Python demonstration.



The demo table is separate from the attribution models so that the ingestion exercise does not alter the historical attribution results.



\## 5. Attribution Rules



The attribution models use a 14-day lookback window before each purchase conversion.



\- \*\*First-Click:\*\* Assigns the earliest eligible marketing touchpoint within the lookback window.

\- \*\*Last-Click:\*\* Assigns the latest eligible marketing touchpoint within the lookback window.

\- \*\*Unattributed conversions:\*\* Remain unattributed when no eligible touchpoint is available within the window.



The models use the available user identifier and conversion timestamp to associate touchpoints with conversions. Identity resolution across devices or identities is not implemented.



When multiple eligible touchpoints have identical timestamps, the selection logic should use a deterministic secondary ordering where supported by the available fields. This is an area to verify and strengthen before production use.



\## 6. Data Quality and Validation



The configured dbt tests check non-null requirements for:



\- Purchase conversion timestamp.

\- Purchase conversion user identifier.

\- Attribution mart purchase timestamp.

\- Attribution mart user identifier.



The tests passed in the validated development run.



The attribution mart contained 5,692 conversion records in that run. First-Click attributed 5,400 records and Last-Click attributed 5,400 records. The remaining 292 conversions had no eligible touchpoint under the configured attribution rules.



These counts describe the data at the time of validation and may change if the source data or models change.



\## 7. Demo Event Ingestion



The Python ingestion script prepares five sample events and loads them into `streaming\_demo\_events` using a BigQuery batch-load job.



The verification script queries the table and displays the inserted records. The dashboard also queries this table to show the latest demo events.



The current environment rejected BigQuery streaming inserts because they were unavailable under the free-tier restrictions encountered during development. For that reason, the demonstration uses batch loading.



The script checks for existing event identifiers before loading new records. This provides a basic repeat-run safeguard, but it does not guarantee exactly-once processing under concurrent execution or every failure scenario.



\## 8. Dashboard



The Streamlit dashboard queries BigQuery directly and presents:



\- Total purchase conversions.

\- First-Click and Last-Click attributed counts.

\- An attributed versus unattributed comparison.

\- A conversion trend over the latest 14-day period represented in the data.

\- First-Click conversion counts by source.

\- A table of demo events loaded into BigQuery.



The trend uses the latest date present in the attribution dataset rather than assuming the sample data is current. The dashboard is intended for assessment demonstration, not production operations.



\## 9. Execution Flow



1\. Configure Python dependencies and BigQuery authentication.

2\. Run the dbt models to build the staging, intermediate, and mart relations.

3\. Run dbt tests to validate the configured data quality requirements.

4\. Execute the Python demo ingestion script to load sample events.

5\. Execute the verification script to confirm that the demo events are visible.

6\. Start Streamlit and inspect the attribution metrics and demo event table.



See the root `README.md` for the exact commands and environment-specific instructions.



\## 10. Limitations and Future Improvements



The current implementation is an assessment-scale pipeline using historical sample data and a small batch ingestion demonstration.



Potential improvements include:



\- Add a true streaming ingestion service when the environment supports it.

\- Strengthen idempotency and retry handling for event ingestion.

\- Add uniqueness and attribution consistency tests.

\- Define and test deterministic tie-breakers for equal-timestamp touchpoints.

\- Improve identity resolution where appropriate identifiers are available.

\- Add data freshness monitoring, operational alerts, and query-cost controls.

\- Consider incremental models and partition-aware processing for larger datasets.



\## 11. Cost and Operational Considerations



BigQuery queries and storage can incur costs depending on usage and billing configuration. The project uses a small assessment-scale demo and should avoid unnecessary full-table queries when possible.



The Python event demo uses a batch-load job rather than streaming inserts. The dashboard issues queries when its page runs or is refreshed. For production, query frequency, scanned bytes, partitioning, caching, and refresh behavior should be reviewed to control cost.



\## 12. Implementation Status



The dbt attribution models, configured data tests, Python batch-ingestion demo, verification script, Streamlit dashboard, and project README have been implemented and pushed to GitHub.



The architecture diagram documents the current implementation. The batch ingestion limitation is stated explicitly rather than presenting the demonstration as a live streaming pipeline.

