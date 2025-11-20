CREATE TABLE `stockpilot-app-478511.stock_analytics_dev.bronze_layer_table` (
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
