WITH ranked_touches AS (

    SELECT
        user_pseudo_id,
        purchase_timestamp,
        purchase_date,
        transaction_id,
        purchase_revenue,
        source,
        medium,
        campaign,
        channel,
        first_touch_rank,
        last_touch_rank

    FROM {{ ref('int_attribution_touches') }}

),

first_click AS (

    SELECT
        user_pseudo_id,
        purchase_timestamp,
        transaction_id,
        source AS first_click_source,
        medium AS first_click_medium,
        campaign AS first_click_campaign,
        channel AS first_click_channel

    FROM ranked_touches
    WHERE first_touch_rank = 1

),

last_click AS (

    SELECT
        user_pseudo_id,
        purchase_timestamp,
        transaction_id,
        source AS last_click_source,
        medium AS last_click_medium,
        campaign AS last_click_campaign,
        channel AS last_click_channel

    FROM ranked_touches
    WHERE last_touch_rank = 1

),

purchases AS (

    SELECT DISTINCT
        user_pseudo_id,
        purchase_timestamp,
        purchase_date,
        transaction_id,
        purchase_revenue

    FROM ranked_touches

)

SELECT
    p.user_pseudo_id,
    p.purchase_timestamp,
    p.purchase_date,
    p.transaction_id,
    p.purchase_revenue,

    f.first_click_source,
    f.first_click_medium,
    f.first_click_campaign,
    f.first_click_channel,

    l.last_click_source,
    l.last_click_medium,
    l.last_click_campaign,
    l.last_click_channel

FROM purchases p

LEFT JOIN first_click f
ON p.user_pseudo_id = f.user_pseudo_id
AND p.purchase_timestamp = f.purchase_timestamp

LEFT JOIN last_click l
ON p.user_pseudo_id = l.user_pseudo_id
AND p.purchase_timestamp = l.purchase_timestamp