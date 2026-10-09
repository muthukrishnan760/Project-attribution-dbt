
WITH purchases AS (

    SELECT
        user_pseudo_id,
        conversion_timestamp_micros AS purchase_timestamp,
        conversion_date AS purchase_date,
        transaction_id,
        conversion_revenue AS purchase_revenue

    FROM {{ ref('int_purchase_conversions') }}

),


touchpoints AS (

    SELECT
        user_pseudo_id,
        event_timestamp AS touchpoint_timestamp,
        event_date AS touchpoint_date,
        event_name AS touchpoint_event,
        source,
        medium,
        campaign,
        channel

    FROM {{ ref('int_marketing_touchpoints') }}

),

matched_touches AS (

    SELECT
        p.user_pseudo_id,
        p.purchase_timestamp,
        p.purchase_date,
        p.transaction_id,
        p.purchase_revenue,

        t.touchpoint_timestamp,
        t.touchpoint_date,
        t.touchpoint_event,
        t.source,
        t.medium,
        t.campaign,
        t.channel,

        ROW_NUMBER() OVER (
            PARTITION BY
                p.user_pseudo_id,
                p.purchase_timestamp,
                p.transaction_id
            ORDER BY
                t.touchpoint_timestamp ASC
        ) AS first_touch_rank,

        ROW_NUMBER() OVER (
            PARTITION BY
                p.user_pseudo_id,
                p.purchase_timestamp,
                p.transaction_id
            ORDER BY
                t.touchpoint_timestamp DESC
        ) AS last_touch_rank

    FROM purchases p

    LEFT JOIN touchpoints t
        ON p.user_pseudo_id = t.user_pseudo_id
        AND t.touchpoint_timestamp < p.purchase_timestamp
        AND t.touchpoint_timestamp >=
            p.purchase_timestamp - (14 * 24 * 60 * 60 * 1000000)

)

SELECT
    user_pseudo_id,
    purchase_timestamp,
    purchase_date,
    transaction_id,
    purchase_revenue,

    touchpoint_timestamp,
    touchpoint_date,
    touchpoint_event,
    source,
    medium,
    campaign,
    channel,

    first_touch_rank,
    last_touch_rank

FROM matched_touches
