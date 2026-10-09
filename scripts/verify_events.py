
from google.cloud import bigquery

PROJECT_ID = "storied-precept-511013-d2"
TABLE_ID = f"{PROJECT_ID}.labsattribution_dbt.streaming_demo_events"

client = bigquery.Client(project=PROJECT_ID)

query = f"""
    SELECT
        event_id,
        user_pseudo_id,
        event_name,
        source,
        medium,
        event_value
    FROM `{TABLE_ID}`
    WHERE event_id LIKE 'demo_%'
    ORDER BY event_id
"""

for row in client.query(query).result():
    print(dict(row))
