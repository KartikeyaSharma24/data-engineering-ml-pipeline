# Real-Time Data Pipeline with Predictive Analytics (Spark + Snowflake + Streamlit)

An end-to-end, cloud-only, free-tier project that ingests stock price data, processes it with Spark on Databricks, generates forecasts with Prophet/ARIMA, stores curated datasets in Snowflake, and serves a dashboard on Streamlit Cloud.

## Architecture
Data → Databricks (Bronze/Silver/Gold) → ML Forecast → Snowflake → Streamlit Dashboard

## Tech Stack
- Databricks Free Edition
- Snowflake Free Tier
- Streamlit Cloud
- GitHub Actions

## Repo Structure
data-engineering-ml-pipeline/
├─ data/
├─ notebooks/
├─ dashboards/
├─ src/
├─ infra/
├─ configs/
├─ tests/
├─ .github/workflows/

## Setup
1. Upload `data/stocks_aapl.csv`.
2. Run Databricks notebooks for ETL + ML.
3. Push curated tables to Snowflake.
4. Deploy Streamlit dashboard from this repo.

## Security
- No secrets in code. Use Streamlit Cloud Secrets.

## Resume Highlights
- Built real-time pipeline using Spark, ML forecasting, Snowflake, and Streamlit.
