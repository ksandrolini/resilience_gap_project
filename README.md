# Resilience Gap Project

An analytics engineering pipeline built using **dbt Core** and **PostgreSQL** to clean, transform, and analyze data from the European Social Survey (Round 11).

## 📂 Project Structure & Data Pipeline

This repository contains the core dbt transformation layer. The raw data itself is kept locally and excluded from version control to comply with file size constraints and data privacy best practices.

* **`models/`**: Contains the SQL transformation scripts (Staging and Marts layers).
* **`ESS_raw_data/`** *(Local Only / Not in Repo)*: External directory on the host machine housing the raw source survey CSV/Excel data files before they are ingested into PostgreSQL.
