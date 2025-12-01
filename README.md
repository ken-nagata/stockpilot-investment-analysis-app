# stockpilot-investment-analysis-app
Turning near real-time market data into simple, actionable investment decisions by automating ingestion, cleaning, feature engineering, and visualization through a modern data-engineering stack.


```markdown
## Architecture Overview

```mermaid
flowchart TD
    A[Airflow DAGs<br/>(Scheduler)] --> I[Ingestion Scripts<br/>(Python)]
    A --> D[dbt Models<br/>(Transform)]
    I --> GCS[Google Cloud Storage<br/>(Raw/Bronze)]
    D --> BQ[BigQuery Tables<br/>Silver/Gold]
    BQ --> UI[Streamlit App<br/>(Analytics UI)]
