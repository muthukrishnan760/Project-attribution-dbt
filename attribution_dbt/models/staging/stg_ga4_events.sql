
WITH source_events AS (

    SELECT
        event_date,
        event_timestamp,
        event_name,
        user_pseudo_id,

        (
            SELECT value.string_value
            FROM UNNEST(event_params)
            WHERE key = 'source'
            LIMIT 1
        ) AS raw_source,

        (
            SELECT value.string_value
            FROM UNNEST(event_params)
            WHERE key = 'medium'
            LIMIT 1
        ) AS raw_medium,

        (
            SELECT value.string_value
            FROM UNNEST(event_params)
            WHERE key = 'campaign'
            LIMIT 1
        ) AS raw_campaign,

        ecommerce.transaction_id AS transaction_id,
        ecommerce.purchase_revenue AS purchase_revenue

    FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`

),

normalized_events AS (

    SELECT
        event_date,
        event_timestamp,
        event_name,
        user_pseudo_id,
        transaction_id,
        purchase_revenue,

        CASE
            WHEN raw_source IS NULL
                OR TRIM(raw_source) IN ('', '<Other>', '(data deleted)')
                THEN NULL
            ELSE LOWER(TRIM(raw_source))
        END AS source,

        CASE
            WHEN raw_medium IS NULL
                OR TRIM(raw_medium) IN ('', '<Other>', '(data deleted)')
                THEN NULL
            ELSE LOWER(TRIM(raw_medium))
        END AS medium,

        CASE
            WHEN raw_campaign IS NULL
                OR TRIM(raw_campaign) IN ('', '<Other>', '(data deleted)')
                THEN NULL
            ELSE LOWER(TRIM(raw_campaign))
        END AS campaign

    FROM source_events

)

SELECT *
FROM normalized_events
