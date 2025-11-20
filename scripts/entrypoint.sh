#!/usr/bin/env bash

airflow db migrate

airflow users create \
  --username admin \
  --password admin \
  --firstname API \
  --lastname Admin \
  --role Admin \
  --email admin@example.com || true

airflow api-server
