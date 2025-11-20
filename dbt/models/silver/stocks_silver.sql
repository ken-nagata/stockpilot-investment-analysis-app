{{ config(
  materialized = 'incremental'
) }}

WITH base AS (
SELECT
  CAST(date_time AS TIMESTAMP) AS date_time,
  upper(ticker) AS ticker,
  name,
  currency,
  CAST(open AS FLOAT64) AS open,
  CAST(high AS FLOAT64) AS high,
  CAST(low AS FLOAT64) AS low,
  CAST(close AS FLOAT64) AS close,
  CAST(adj_close AS FLOAT64) AS adj_close,
  CAST(volume AS INT64) AS volume,
  source,
  date,
  ingested_at
FROM {{ source("raw","bronze_data") }}
),

rounding_columns AS (
SELECT
  date_time,
  ticker,
  name,
  currency,
  ROUND(open,2) AS open,
  ROUND(high,2) AS high,
  ROUND(low,2) AS low,
  ROUND(close,2) AS close,
  ROUND(adj_close,2) AS adj_close,
  volume,
  source,
  date,
  ingested_at,
  concat(ticker, '#', cast(date_time as string)) as event_key
FROM base
),

ranked as (
  select
    *,
    row_number() over (
      partition by event_key
      order by ingested_at desc
    ) as rn
  from rounding_columns
)


select *
from ranked
where rn = 1
