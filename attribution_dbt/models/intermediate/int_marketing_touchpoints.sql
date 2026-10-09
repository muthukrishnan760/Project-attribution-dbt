
WITH staged_events AS (

    SELECT
        event_date,
        event_timestamp,
        event_name,
        user_pseudo_id,
        source,
        medium,
        campaign

    FROM {{ ref('stg_ga4_events') }}

),

normalized_touchpoints AS (

    SELECT
        event_date,
        event_timestamp,
        event_name,
        user_pseudo_id,

        NULLIF(LOWER(TRIM(source)), '') AS source,
        NULLIF(LOWER(TRIM(medium)), '') AS medium,
        NULLIF(TRIM(campaign), '') AS campaign

    FROM staged_events

    WHERE
        event_name != 'purchase'
        AND user_pseudo_id IS NOT NULL

),

eligible_touchpoints AS (

    SELECT
        event_date,
        event_timestamp,
        event_name,
        user_pseudo_id,
        source,
        medium,
        campaign,

        CASE
            WHEN source IS NULL OR medium IS NULL
                THEN 'unknown'
            WHEN source = '<other>'
                OR medium = '<other>'
                OR source = '(data deleted)'
                OR medium = '(data deleted)'
                THEN 'unknown'
            WHEN source = '(direct)'
                OR medium = '(none)'
                THEN 'direct'
            ELSE CONCAT(source, ' / ', medium)
        END AS channel

    FROM normalized_touchpoints

)

SELECT
    event_date,
    event_timestamp,
    event_name,
    user_pseudo_id,
    source,
    medium,
    campaign,
    channel

FROM eligible_touchpoints

WHERE channel NOT IN ('unknown')