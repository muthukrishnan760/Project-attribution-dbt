
WITH first_touch AS (
    SELECT
        user_pseudo_id,
        purchase_timestamp,
        purchase_date,
        transaction_id,
        purchase_revenue,
        source,
        medium,
        campaign,
        channel
    FROM {{ ref('int_attribution_touches') }}
    WHERE first_touch_rank = 1
)

SELECT
    channel,
    COUNT(*) AS attributed_conversions,
    SUM(purchase_revenue) AS attributed_revenue,
    COUNT(DISTINCT user_pseudo_id) AS attributed_users
FROM first_touch
GROUP BY channel
