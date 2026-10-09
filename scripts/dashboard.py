
import streamlit as st
import pandas as pd
from google.cloud import bigquery

PROJECT_ID = "storied-precept-511013-d2"
DATASET_ID = "labsattribution_dbt"
MART = f"{PROJECT_ID}.{DATASET_ID}.mart_attribution"
EVENTS = f"{PROJECT_ID}.{DATASET_ID}.streaming_demo_events"

st.set_page_config(page_title="Marketing Attribution Dashboard", layout="wide")
st.title("Marketing Attribution Dashboard")
st.caption("First-click vs last-click attribution | BigQuery + dbt")


@st.cache_resource
def get_client():
    return bigquery.Client(project=PROJECT_ID)


client = get_client()


def query_df(sql):
    return client.query(sql).to_dataframe()


try:
    totals_sql = f"""
        SELECT
            COUNT(*) AS total_conversions,
            COUNTIF(first_click_source IS NOT NULL) AS first_attributed,
            COUNTIF(last_click_source IS NOT NULL) AS last_attributed,
            COUNTIF(first_click_source IS NULL) AS first_unattributed,
            COUNTIF(last_click_source IS NULL) AS last_unattributed
        FROM `{MART}`
    """
    totals = query_df(totals_sql).iloc[0]

    a, b, c = st.columns(3)
    a.metric("Total conversions", f"{int(totals['total_conversions']):,}")
    b.metric("First-click attributed", f"{int(totals['first_attributed']):,}")
    c.metric("Last-click attributed", f"{int(totals['last_attributed']):,}")

    st.subheader("Attribution comparison")
    comparison = pd.DataFrame(
        {
            "Attributed": [
                int(totals["first_attributed"]),
                int(totals["last_attributed"]),
            ],
            "Unattributed": [
                int(totals["first_unattributed"]),
                int(totals["last_unattributed"]),
            ],
        },
        index=["First Click", "Last Click"],
    )
    st.bar_chart(comparison)

    st.subheader("Conversions over the latest 14 days in the dataset")
    trend_sql = f"""
        WITH latest_date AS (
            SELECT MAX(DATE(TIMESTAMP_MICROS(purchase_timestamp))) AS max_date
            FROM `{MART}`
        )
        SELECT
            DATE(TIMESTAMP_MICROS(purchase_timestamp)) AS conversion_date,
            COUNT(*) AS conversions,
            COUNTIF(first_click_source IS NOT NULL) AS first_click_attributed,
            COUNTIF(last_click_source IS NOT NULL) AS last_click_attributed
        FROM `{MART}`
        WHERE DATE(TIMESTAMP_MICROS(purchase_timestamp)) >=
              DATE_SUB((SELECT max_date FROM latest_date), INTERVAL 13 DAY)
          AND DATE(TIMESTAMP_MICROS(purchase_timestamp)) <=
              (SELECT max_date FROM latest_date)
        GROUP BY conversion_date
        ORDER BY conversion_date
    """
    trend = query_df(trend_sql)
    if trend.empty:
        st.info("No conversion dates are available in the attribution table.")
    else:
        st.line_chart(
            trend.set_index("conversion_date")[
                ["first_click_attributed", "last_click_attributed"]
            ]
        )

    st.subheader("First-click conversions by source")
    source_sql = f"""
        SELECT
            COALESCE(first_click_source, 'Unattributed') AS source,
            COUNT(*) AS conversions
        FROM `{MART}`
        GROUP BY source
        ORDER BY conversions DESC
    """
    source_data = query_df(source_sql)
    st.bar_chart(source_data.set_index("source"))
    st.dataframe(source_data, use_container_width=True)

    st.subheader("Demo event ingestion")
    st.caption("Batch-loaded events; this is not a live streaming feed.")
    events_sql = f"""
        SELECT
            event_timestamp, event_id, user_pseudo_id, event_name,
            source, medium, campaign, event_value, ingested_at
        FROM `{EVENTS}`
        ORDER BY ingested_at DESC
        LIMIT 100
    """
    events = query_df(events_sql)
    st.metric("Demo events visible", len(events))
    st.dataframe(events, use_container_width=True)

    if st.button("Refresh dashboard"):
        st.rerun()

except Exception as exc:
    st.error("The dashboard could not query BigQuery.")
    st.exception(exc)
