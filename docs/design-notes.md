\# Attribution Pipeline — Design Notes



\## 1. Overview



While building this project, I wanted to keep the attribution logic simple enough to understand and test. I used dbt to organise the transformations and BigQuery to store the results. The Streamlit dashboard brings the main attribution numbers together so they are easier to compare.



This document explains how I have organised the pipeline, how the two attribution models work, and a few things I would improve if I continued developing the project.



\## 2. How the Attribution Pipeline Works



I split the transformations into smaller models so that each step has a clear purpose.



```text

&#x20;       GA4 Public Dataset

&#x20;               |

&#x20;               v

&#x20;         stg\_ga4\_events

&#x20;               |

&#x20;       +-------+--------+

&#x20;       |                |

&#x20;       v                v

&#x20;Purchase Conversions  Marketing Touchpoints

&#x20;       |                |

&#x20;       +-------+--------+

&#x20;               |

&#x20;               v

&#x20;     int\_attribution\_touches

&#x20;               |

&#x20;       +-------+--------+

&#x20;       |                |

&#x20;       v                v

&#x20;   First-Click       Last-Click

&#x20;  Attribution       Attribution

&#x20;       |                |

&#x20;       v                v

&#x20; First-Click Mart  Last-Click Mart

&#x20;       |                |

&#x20;       +-------+--------+

&#x20;               |

&#x20;               v

&#x20;      mart\_attribution

&#x20;               |

&#x20;               v

&#x20;      Streamlit Dashboard

```



I kept the purchase conversions and marketing touchpoints separate before matching them. This makes it easier to follow where the data comes from and troubleshoot a problem if the attribution results look wrong.



\### How I assign attribution



For this project, I used a 14-day lookback window before each purchase.



\- \*\*First-Click:\*\* Gives credit to the earliest eligible marketing touchpoint in the window.

\- \*\*Last-Click:\*\* Gives credit to the latest eligible marketing touchpoint in the window.

\- \*\*Unattributed purchases:\*\* If no eligible touchpoint is found, the purchase remains unattributed.

\- \*\*User matching:\*\* I use the pseudonymous user identifier available in the GA4 data. This does not identify the same person across different devices or browsers.

\- \*\*Event ordering:\*\* I use event timestamps to determine which touchpoint came first or last. Events with identical timestamps may need an additional tie-breaker to guarantee a consistent order.



Both models assign full credit to their selected touchpoint. I kept them as separate models so that the results can be compared rather than splitting credit between them.



\### Results I checked



When I checked the models against the available dataset, I got the following results:



| Metric | Count |

|---|---:|

| Total purchase conversions | 5,692 |

| First-Click attributed | 5,400 |

| Last-Click attributed | 5,400 |

| Unattributed purchases | 292 |



The two attribution models have the same number of attributed purchases, but they do not necessarily select the same marketing touchpoint for each purchase.



\## 3. Dashboard Sketch



I kept the dashboard focused on the main questions: how many purchases occurred, how the two attribution models compare, which sources receive credit, and whether the sample events have reached BigQuery.



```text

+------------------------------------------------------+

|          CustomerLabs Attribution Dashboard          |

|                                                      |

| +---------------+ +---------------+ +--------------+ |

| | Total         | | First-Click   | | Last-Click   | |

| | Conversions   | | Attributed    | | Attributed   | |

| |    5,692      | |    5,400      | |    5,400     | |

| +---------------+ +---------------+ +--------------+ |

|                                                      |

|        First-Click vs Last-Click Comparison          |

|                                                      |

|        Purchase Trend — Latest Available 14 Days     |

|                                                      |

|        Conversion Breakdown by Source                |

|                                                      |

|        Sample Events Loaded into BigQuery            |

|                                                      |

+------------------------------------------------------+

```



This is a sketch of the dashboard layout, not a screenshot. The numbers are from my current validation run and may change if the underlying data changes.



The dashboard includes:



\- Summary numbers for total purchases and attributed purchases.

\- A comparison of First-Click and Last-Click results.

\- A purchase trend covering the latest available 14-day period in the dataset.

\- A breakdown of attribution by source.

\- A panel showing the sample events loaded into the separate BigQuery demo table.



The trend uses the latest dates available in the dataset, so it should not be interpreted as necessarily covering the last 14 calendar days from today.



\## 4. Sample Event Ingestion



I also added a small Python script to generate five sample events and load them into BigQuery.



```text

&#x20;     Python Script

&#x20;           |

&#x20;           v

&#x20;    Create 5 Events

&#x20;           |

&#x20;           v

&#x20;   BigQuery Batch Load

&#x20;           |

&#x20;           v

&#x20; streaming\_demo\_events

&#x20;           |

&#x20;      +----+-----+

&#x20;      |          |

&#x20;      v          v

&#x20;   Verify     Dashboard

&#x20;   Script     Event Panel

```



I used a batch-load job for this demonstration because that was the ingestion method available in my current environment. The `verify\_events.py` script checks whether the events were loaded successfully.



This is a working batch-ingestion demo, not a continuous streaming pipeline. The sample events are separate from the GA4 attribution data, so loading them does not automatically change the attribution totals.



If I extended this part of the project, I would add stronger duplicate handling and make retries safer. I would also look at a streaming-capable ingestion method if lower event latency were required.



\## 5. Things I Would Improve Next



There are a few areas I would work on before treating this as a production pipeline.



\- \*\*Duplicate events:\*\* Make ingestion retries safe by enforcing a clear event-ID-based deduplication strategy.

\- \*\*Timestamp ties:\*\* Add a stable secondary ordering key where the source data supports it.

\- \*\*Identity resolution:\*\* Handle cross-device identity only if reliable identifiers and an appropriate identity policy are available.

\- \*\*Streaming:\*\* Replace the batch-load demo with a streaming-capable ingestion path and measure the actual ingestion latency.

\- \*\*Monitoring:\*\* Add checks for failed loads, stale data, duplicate events, and failed dbt tests.

\- \*\*Cost:\*\* Keep queries limited to the required columns and date ranges, and monitor BigQuery usage.



I would prioritise reliable ingestion and duplicate handling before adding more complicated attribution models.



\## 6. Current Scope



The project currently includes the dbt transformations, First-Click and Last-Click attribution models, data tests, a Streamlit dashboard, and a small batch-ingestion demo.



The main limitation is that the event demo is not true streaming, and the current implementation does not guarantee exactly-once processing in every retry or concurrent-run scenario. I have kept these limitations explicit rather than presenting them as completed features.

