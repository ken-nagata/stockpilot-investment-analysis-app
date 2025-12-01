{{ config(
    materialized= 'table',
    cluster_by=['ticker'],
    on_schema_change='sync_all_columns')
}}

{% set eps = 1e-6 %}

WITH ranked AS (
  SELECT
    *,
    row_number() over (partition by event_key order by ingested_at desc) as row_nb
  FROM {{ ref('stocks_silver') }}
),
base_silver AS (
  SELECT *
  FROM ranked
  WHERE row_nb = 1
),
base AS (
    SELECT
        *,
        CASE WHEN close < low - {{eps}} THEN low
        WHEN close > high + {{eps}} THEN high
        ELSE close
        END AS close_fixed
    FROM base_silver
),
features AS (
    SELECT
        *
        ,LAG(close) OVER(PARTITION BY ticker ORDER BY date_time) AS prev_close
        ,LAG(high) OVER(PARTITION BY ticker ORDER BY date_time) AS prev_high
        ,LAG(low) OVER(PARTITION BY ticker ORDER BY date_time) AS prev_low
        ,LAG(volume) OVER(PARTITION BY ticker ORDER BY date_time) AS prev_volume
    FROM base
),
returns AS (
    SELECT
        *
        ,SAFE_DIVIDE(close - prev_close, prev_close) AS return_
        ,(close - prev_close) AS price_change
    FROM features
),

 ------ 14-minute Relative Strength Index (RSI) ------
rsi_prep AS (
    SELECT
        *
        ,CASE WHEN price_change > 0 THEN price_change ELSE 0 END AS gain
        ,CASE WHEN price_change < 0 THEN price_change ELSE 0 END AS loss
    FROM returns
),
rsi_int AS (
    SELECT
        *
        ,AVG(gain) OVER(PARTITION BY ticker ORDER BY date_time ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) AS avg_gain14
        ,AVG(loss) OVER(PARTITION BY ticker ORDER BY date_time ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) AS avg_loss14
    FROM rsi_prep
),

-- rsi_final AS (
--     SELECT
--         *,
--         CASE
--             WHEN avg_loss14 IS NULL OR avg_loss14 = 0 THEN 100.0
--             WHEN avg_gain14 IS NULL THEN 0
--             ELSE 100.0 - 100.0 / (1.0 + avg_gain14 / avg_loss14)
--         END AS rsi_14
--     FROM rsi_int
-- ),

---- Average True Range (ATR) ------
atr_calc AS (
    SELECT
        *
        ,GREATEST(
            high - low,
            ABS(high - prev_close),
            ABS(low - prev_close)
        ) AS true_range
    FROM rsi_int
),
atr_final AS (
    SELECT
        *
        ,AVG(true_range) OVER(PARTITION BY ticker ORDER BY date ROWS BETWEEN  13 PRECEDING AND CURRENT ROW) AS atr_14
    FROM atr_calc
),

------ Moving Averages 9m/21m------
mas AS (
    SELECT
        *
        ,AVG(close) OVER(PARTITION BY ticker ORDER BY date_time ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS sma_9
        ,AVG(close) OVER(PARTITION BY ticker ORDER BY date_time ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) AS sma_21
    FROM atr_final
),

------ Volume Metrics ------
vol_metrics AS (
    SELECT
        *
        ,AVG(volume) OVER(PARTITION BY ticker ORDER BY date_time ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) AS vol_sma21
        ,SAFE_DIVIDE(volume, NULLIF(AVG(volume) OVER(PARTITION BY ticker ORDER BY date ROWS BETWEEN 20 PRECEDING AND CURRENT ROW),0)) AS vol_ratio
    FROM mas
)

------ Volume Metrics ------
    SELECT
        ticker
        ,date_time
        ,open
        ,high
        ,low
        ,close
        ,close_fixed
        ,volume
        ,prev_close
        ,prev_high
        ,prev_low
        ,prev_volume
        ,ROUND(price_change,2) AS price_change
        ,ROUND(return_,4) AS return_
        ,ROUND(avg_gain14,2) AS avg_gain14
        ,ROUND(avg_loss14,2) AS avg_loss14
        -- trend/levels
        ,ROUND(sma_9,2) AS sma_9
        ,ROUND(sma_21,2) AS sma_21
        -- momentum
        -- ,ROUND(rsi_14,2) AS rsi_14
        -- volatility
        ,ROUND(atr_14,2) AS atr_14
        -- volume
        ,ROUND(vol_sma21,2) AS vol_sma21
        ,ROUND(vol_ratio,2) AS vol_ratio
    FROM vol_metrics
