# stockpilot-investment-analysis-app
Turning near real-time market data into simple, actionable investment decisions by automating ingestion, cleaning, feature engineering, and visualization through a modern data-engineering stack.



                   ┌─────────────────────────┐
                   │       Airflow DAGs       │
                   │ (Orchestration / Scheduler)│
                   └──────────────┬───────────┘
                                  │
        ┌─────────────────────────┼───────────────────────────┐
        │                         │                           │
        ▼                         ▼                           ▼
┌────────────────┐      ┌────────────────┐         ┌──────────────────────┐
│ Ingestion Code │      │     dbt        │         │ Google Cloud Storage │
│  (Python)      │      │ (Transform)    │         │ (Raw / Bronze Layer) │
└───────┬────────┘      └──────┬─────────┘         └──────────┬──────────┘
        │                       │                              │
        │                       ▼                              │
        │             ┌────────────────────┐                   │
        └────────────►│   BigQuery Tables  │◄──────────────────┘
                      │ Bronze / Silver /  │
                      │       Gold         │
                      └─────────┬──────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │    Streamlit App    │
                     │ (Analytics Frontend)│
                     └─────────────────────┘
