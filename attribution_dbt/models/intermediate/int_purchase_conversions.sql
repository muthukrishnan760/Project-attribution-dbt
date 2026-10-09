
WITH purchase_events AS (

    SELECT
        user_pseudo_id,
        event_timestamp,
        event_date,
        transaction_id,
        purchase_revenue

    FROM {{ ref('stg_ga4_events') }}

    WHERE event_name = 'purchase'

)

SELECT
    user_pseudo_id,

    -- GA4 timestamps are stored in microseconds.
    TIMESTAMP_MICROS(event_timestamp) AS conversion_timestamp,

    event_timestamp AS conversion_timestamp_micros,
    event_date AS conversion_date,
    transaction_id,
    purchase_revenue AS conversion_revenue
FROM purchase_events
