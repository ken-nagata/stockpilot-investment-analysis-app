#!/usr/bin/env bash

airflow db migrate

airflow users create -r Admin  -u $AIRFLOW_ADMIN_USERNAME -p $AIRFLOW_ADMIN_PASSWORD -e $AIRFLOW_ADMIN_EMAIL -f $AIRFLOW_ADMIN_FIRSTNAME -l $AIRFLOW_ADMIN_LASTNAME

airflow webserver
