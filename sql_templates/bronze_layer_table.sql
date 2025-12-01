CREATE TABLE `{PROJECT_ID}.{DATASET}.{BRONZE_TABLE}` (
  date_time   TIMESTAMP,
  ticker      STRING,
  name        STRING,
  currency    STRING,
  open        FLOAT64,
  high        FLOAT64,
  low         FLOAT64,
  close       FLOAT64,
  adj_close   FLOAT64,
  volume      INT64,
  source      STRING,
  date        DATE,
  ingested_at TIMESTAMP
)
PARTITION BY DATE(date_time)
CLUSTER BY ticker;
