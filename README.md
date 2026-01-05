# 📈 Stock Price Forecasting Pipeline

**Live App:** <https://data-engineering-ml-pipeline.streamlit.app/>  
**Tech Stack:** Databricks | Snowflake | Streamlit Cloud | Python | Plotly

***

## ✅ Overview

This project demonstrates an **end-to-end cloud data pipeline** for **stock price analysis and forecasting**.  
It integrates:

*   **Databricks** for data preparation and forecasting
*   **Snowflake** for cloud data storage
*   **Streamlit Cloud** for interactive visualization

The app allows users to:

*   View **historical stock prices** (Actuals)
*   Explore **forecasted prices** (Predictions)
*   Compare both on an **overlay chart**

***

## 📊 Dataset

We used **S\&P 500 stock prices (2014–2017)**, which includes:

*   `symbol` → Company ticker (e.g., AAPL, MSFT)
*   `date` → Trading day
*   `open`, `high`, `low`, `close` → Daily price points
*   `volume` → Shares traded

This dataset helps demonstrate:

*   **Historical trends** in stock prices
*   How forecasting models predict future movements

***

## 🏗️ Architecture

    Databricks → Snowflake → Streamlit Cloud

*   **Databricks:** Cleans raw CSV, computes returns, trains forecasting model (Prophet/ARIMA)
*   **Snowflake:** Stores actuals (`STOCK_SILVER`) and forecasts (`STOCK_FORECAST`)
*   **Streamlit:** Displays charts and insights in a web app

***

## 🔍 Features

*   **Symbol Selector:** Choose any ticker from actuals or forecast tables
*   **Date Range Filter:** Focus on specific periods
*   **Charts:**
    *   **Overlay Chart:** Actual vs Forecast
    *   **Actuals Panel:** Historical closing prices
    *   **Forecast Panel:** Predicted prices (+ confidence intervals)
*   **Dynamic Updates:** App refreshes based on user input
*   **Error Handling:** Friendly messages for missing data or forecasts

***

## 🚀 How It Works

1.  **Data Prep:**
    *   Load S\&P 500 CSV into Databricks
    *   Clean and calculate returns
    *   Train forecasting model for selected symbols
2.  **Data Storage:**
    *   Push actuals and forecasts into Snowflake tables
3.  **Visualization:**
    *   Streamlit app queries Snowflake
    *   Displays interactive charts using Plotly

***

## 📈 What Do the Graphs Show?

*   **Actual Close Price:** Real historical trend
*   **Forecast Price:** Model prediction for future dates
*   **Overlay:** Compare actual vs forecast visually
    *   **Upward trend:** Company growth
    *   **Downward trend:** Possible decline

***

## ✅ Current Scope

*   Forecast available for **AAPL** (Apple)
*   Actuals available for multiple S\&P 500 tickers
*   Easily extend forecasts by running the same pipeline for more symbols

***

## 🛠️ Tech Highlights

*   **Cloud-only deployment** (no local installs)
*   **Caching for performance** (`@st.cache_resource`, `@st.cache_data`)
*   **Dark theme charts** for professional look
*   **Secure secrets management** in Streamlit Cloud

***

## 📌 Future Enhancements

*   Add forecasts for more tickers
*   Enable CSV download for filtered data
*   Add performance metrics (RMSE, MAE)
*   Multi-symbol comparison view

***

## 📷 Screenshots

<img width="1894" height="957" alt="image" src="https://github.com/user-attachments/assets/805e7579-d57a-4a43-8027-5322c5c2421f" />
<img width="1888" height="951" alt="image" src="https://github.com/user-attachments/assets/7b23995f-0841-478a-b9ff-f5a4f02acaf8" />
<img width="1895" height="948" alt="Screenshot 2026-01-05 203958" src="https://github.com/user-attachments/assets/4855d934-4eb8-4a25-8891-57685aeb1936" />


***

## 🙌 Credits

*   Dataset: S\&P 500 daily prices (2014–2017)
*   Tools: Databricks, Snowflake, Streamlit, Plotly
*   Author: **Kartikeya Sharma**

***

### ✅ Why This Project Matters

This project showcases **real-world data engineering and ML skills**:

*   Building pipelines across **multiple cloud platforms**
*   Deploying an **interactive dashboard**
*   Applying **forecasting models** to financial data
