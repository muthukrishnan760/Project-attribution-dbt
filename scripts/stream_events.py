
import json
from datetime import datetime, timezone
from pathlib import Path

from google.cloud import bigquery

PROJECT_ID = "storied-precept-511013-d2"
DATASET_ID = "labsattribution_dbt"
TABLE_ID = f"{PROJECT_ID}.{DATASET_ID}.streaming_demo_events"


def main():
    client = bigquery.Client(project=PROJECT_ID)

    # Give this demo batch a fixed set of event IDs.
    # Existing IDs are checked before loading to avoid simple repeat runs.
    now = datetime.now(timezone.utc).isoformat()

    sample_events = [
        {
            "event_id": "demo_001_page_view",
            "user_pseudo_id": "demo_user_001",
            "event_name": "page_view",
            "event_timestamp": now,
            "source": "google",
            "medium": "organic",
            "campaign": "demo_search",
            "event_value": None,
            "ingested_at": now,
        },
        {
            "event_id": "demo_001_session_start",
            "user_pseudo_id": "demo_user_001",
            "event_name": "session_start",
            "event_timestamp": now,
            "source": "google",
            "medium": "organic",
            "campaign": "demo_search",
            "event_value": None,
            "ingested_at": now,
        },
        {
            "event_id": "demo_002_page_view",
            "user_pseudo_id": "demo_user_002",
            "event_name": "page_view",
            "event_timestamp": now,
            "source": "facebook",
            "medium": "social",
            "campaign": "demo_social",
            "event_value": None,
            "ingested_at": now,
        },
        {
            "event_id": "demo_002_purchase",
            "user_pseudo_id": "demo_user_002",
            "event_name": "purchase",
            "event_timestamp": now,
            "source": "facebook",
            "medium": "social",
            "campaign": "demo_social",
            "event_value": 49.99,
            "ingested_at": now,
        },
        {
            "event_id": "demo_003_page_view",
            "user_pseudo_id": "demo_user_003",
            "event_name": "page_view",
            "event_timestamp": now,
            "source": "newsletter",
            "medium": "email",
            "campaign": "demo_email",
            "event_value": None,
            "ingested_at": now,
        },
    ]

    # Read existing IDs so rerunning this script skips known demo events.
    existing_query = f"""
        SELECT event_id
        FROM `{TABLE_ID}`
        WHERE event_id IN UNNEST(@event_ids)
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter(
                "event_ids",
                "STRING",
                [event["event_id"] for event in sample_events],
            )
        ]
    )

    existing_ids = {
        row.event_id
        for row in client.query(
            existing_query, job_config=job_config
        ).result()
    }

    new_events = [
        event for event in sample_events
        if event["event_id"] not in existing_ids
    ]

    if not new_events:
        print("All demo events already exist. Nothing to load.")
        return

    # Write newline-delimited JSON to a temporary local file.
    # BigQuery loads the file as a batch, not as live streaming.
    temp_file = Path("demo_events_to_load.jsonl")
    with temp_file.open("w", encoding="utf-8") as file:
        for event in new_events:
            file.write(json.dumps(event) + "\n")

    try:
        config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        )

        with temp_file.open("rb") as file:
            load_job = client.load_table_from_file(
                file,
                TABLE_ID,
                job_config=config,
            )

        load_job.result()

        print(f"Loaded {len(new_events)} new events.")
        for event in new_events:
            print(
                f"Loaded: {event['event_name']} "
                f"for {event['user_pseudo_id']}"
            )
        print(f"Destination table: {TABLE_ID}")
    finally:
        temp_file.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
