# stockpilot-investment-analysis-app
Turning near real-time market data into simple, actionable investment decisions by automating ingestion, cleaning, feature engineering, and visualization through a modern data-engineering stack.


## Architecture Overview
```mermaid
flowchart TB

    subgraph PIPELINE[Airflow Orchestration]
        direction LR
        ING[Python API<br/>Extraction] --> GCS[Google Cloud Storage]
        GCS --> DBT_BRONZE[Bronze<br/>Layer]
        subgraph dbt[dbt Transformation]
            DBT_BRONZE --> DBT_SILVER[Silver<br/>Layer]
            DBT_SILVER --> DBT_GOLD[Gold<br/>Layer]
        end
    end
    STREAMLIT[Streamlit App]


    %% Colors
    style ING fill:#34D399,stroke:#059669,stroke-width:2px,color:#000
    style GCS fill:#66A6FF,stroke:#4285F4,stroke-width:2px,color:#fff
    style DBT_BRONZE fill:#fb923c,stroke:#f97316,stroke-width:2px,color:#fff
    style DBT_SILVER fill:#E5E7EB,stroke:#9CA3AF,stroke-width:2px,color:#000
    style DBT_GOLD fill:#FACC15,stroke:#EAB308,stroke-width:2px,color:#000
    style STREAMLIT fill:#FF4B4B,stroke:#E63946,stroke-width:2px,color:#fff
```
