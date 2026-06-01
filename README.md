# Resilience Gap Project

An analytics engineering pipeline built using **dbt Core** and **PostgreSQL** to transform European Social Survey (Round 11) data.

## Project Structure
- `ESS_raw_data/`: Local storage for source survey datasets.
- `dbt/resilience_gap_project/`: The core dbt transformation layer models.

## Setup Instructions
To build the models locally, navigate to the dbt project directory and execute:
```bash
dbt run
