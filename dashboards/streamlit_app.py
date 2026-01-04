
# dashboards/streamlit_app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import snowflake.connector

# 1) Page config
st.set_page_config(page_title="Stocks — Actuals & Forecast", layout="wide")

# 2) Secrets check
if "snowflake" not in st.secrets:
    st.error("Missing [snowflake] secrets in Streamlit Cloud. Go to Settings → Secrets.")
    st.stop()

# 3) Connection as a cached *resource* (hash-safe)
@st.cache_resource
def get_conn():
    sf = st.secrets["snowflake"]
    return snowflake.connector.connect(
        account=sf["account"],
        user=sf["user"],
        password=sf["password"],
        warehouse=sf["warehouse"],
        database=sf["database"],
        schema=sf["schema"],
        role=sf.get("role", None),
    )

conn = get_conn()

# === Snowflake object names based on your SQL ===
DB = "SNOWFLAKE_LEARNING_DB"
SCHEMA = "PUBLIC"
ACTUALS_TABLE = f"{DB}.{SCHEMA}.STOCK_SILVER"     # SNOWFLAKE_LEARNING_DB.PUBLIC.STOCK_SILVER
FORECAST_TABLE = f"{DB}.{SCHEMA}.STOCK_FORECAST"  # SNOWFLAKE_LEARNING_DB.PUBLIC.STOCK_FORECAST

# Column names in actuals table
DATE_COL = "DT"
CLOSE_COL = "CLOSE"
SYMBOL_COL = "SYMBOL"

# 4) Cached helpers (NO connection parameter!)
@st.cache_data(ttl=600)
def list_symbols() -> list[str]:
    sql = f"SELECT DISTINCT SYMBOL FROM {FORECAST_TABLE} ORDER BY SYMBOL"
    cur = conn.cursor()
    cur.execute(sql)
    symbols = [row[0] for row in cur.fetchall()]
    cur.close()
    return symbols

@st.cache_data(ttl=600)
def load_forecast(symbol: str) -> pd.DataFrame:
    sql = f"""
        SELECT 
            TRY_TO_DATE(DS) AS DS,
            TRY_TO_DOUBLE(YHAT) AS YHAT,
            SYMBOL,
            TRY_TO_DOUBLE(YHAT_LOWER) AS YHAT_LOWER,
            TRY_TO_DOUBLE(YHAT_UPPER) AS YHAT_UPPER
        FROM {FORECAST_TABLE}
        WHERE SYMBOL = %(symbol)s
        ORDER BY DS
    """
    cur = conn.cursor()
    cur.execute(sql, {"symbol": symbol})
    rows = cur.fetchall()
    cur.close()
    df = pd.DataFrame(rows, columns=["DS", "YHAT", "SYMBOL", "YHAT_LOWER", "YHAT_UPPER"])
    df["DS"] = pd.to_datetime(df["DS"], errors="coerce")
    df["YHAT"] = pd.to_numeric(df["YHAT"], errors="coerce")
    for c in ["YHAT_LOWER", "YHAT_UPPER"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["DS", "YHAT"])
    return df

@st.cache_data(ttl=600)
def load_actuals(symbol: str) -> pd.DataFrame:
    sql = f"""
        SELECT 
            TRY_TO_DATE({DATE_COL}) AS DS,
            TRY_TO_DOUBLE({CLOSE_COL}) AS CLOSE,
            {SYMBOL_COL} AS SYMBOL
        FROM {ACTUALS_TABLE}
        WHERE {SYMBOL_COL} = %(symbol)s
        ORDER BY {DATE_COL}
    """
    cur = conn.cursor()
    cur.execute(sql, {"symbol": symbol})
    rows = cur.fetchall()
    cur.close()
    df = pd.DataFrame(rows, columns=["DS", "CLOSE", "SYMBOL"])
    df["DS"] = pd.to_datetime(df["DS"], errors="coerce")
    df["CLOSE"] = pd.to_numeric(df["CLOSE"], errors="coerce")
    df = df.dropna(subset=["DS", "CLOSE"])
    return df

# 5) Sidebar — symbol + date range
symbols = list_symbols()
if not symbols:
    st.error("No symbols found in forecast table. Verify your pipeline loaded data.")
    st.stop()

symbol = st.sidebar.selectbox("Symbol", options=symbols, index=0)

# Date range selector based on available data
df_actuals_all = load_actuals(symbol)
if df_actuals_all.empty:
    df_forecast_all = load_forecast(symbol)
    if df_forecast_all.empty:
        st.warning("No data available for this symbol.")
        st.stop()
    min_date = pd.to_datetime(df_forecast_all["DS"].min())
    max_date = pd.to_datetime(df_forecast_all["DS"].max())
else:
    min_date = pd.to_datetime(df_actuals_all["DS"].min())
    max_date = pd.to_datetime(df_actuals_all["DS"].max())

start_date, end_date = st.sidebar.slider(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

# Filtered frames for plotting
df_actuals = df_actuals_all[(df_actuals_all["DS"] >= start_date) & (df_actuals_all["DS"] <= end_date)]
df_forecast_all = load_forecast(symbol)
df_forecast = df_forecast_all[(df_forecast_all["DS"] >= start_date) & (df_forecast_all["DS"] <= end_date)]

# 6) Overlay first
st.header("📈 Stocks — Actuals & Forecast")

fig_overlay = go.Figure()
if not df_actuals.empty:
    fig_overlay.add_trace(go.Scatter(
        x=df_actuals["DS"], y=df_actuals["CLOSE"],
        mode="lines", name="Actual Close",
        line=dict(color="#F72585", width=2)
    ))
if not df_forecast.empty:
    fig_overlay.add_trace(go.Scatter(
        x=df_forecast["DS"], y=df_forecast["YHAT"],
        mode="lines", name="Forecast",
        line=dict(color="#4CC9F0", width=2, dash="dot")
    ))

fig_overlay.update_layout(
    title=f"Actual vs Forecast — {symbol}",
    template="plotly_dark",
    xaxis_title="Date",
    yaxis_title="Price",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig_overlay, use_container_width=True)

# 7) Two panels
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"Actual Close — {symbol}")
    st.caption(f"Actual rows: {len(df_actuals)}")
    if df_actuals.empty:
        st.warning(f"No actuals found for '{symbol}' in selected date range.")
    else:
        fig_actuals = px.line(
            df_actuals,
            x="DS",
            y="CLOSE",
            title=f"Actual Close — {symbol}",
        )
        fig_actuals.update_traces(line=dict(color="#F72585", width=2), opacity=1.0)
        fig_actuals.update_layout(template="plotly_dark", xaxis_title="Date", yaxis_title="Close")
        st.plotly_chart(fig_actuals, use_container_width=True)

with col2:
    st.subheader(f"Forecast — {symbol}")
    with st.expander("Debug (forecast)", expanded=False):
        st.caption(f"Forecast rows: {len(df_forecast)}")
        st.write("Sample forecast rows:", df_forecast.head(5))
        st.write("Dtypes:", df_forecast.dtypes.to_dict())
        st.write("NaN counts:", df_forecast.isna().sum().to_dict())

    if df_forecast.empty or df_forecast["YHAT"].isna().all():
        st.warning(f"No forecast data (or all NaNs) for '{symbol}' in selected date range.")
    else:
        fig_forecast = px.line(
            df_forecast,
            x="DS",
            y="YHAT",
            title=f"Forecast — {symbol}",
        )
        fig_forecast.update_traces(line=dict(color="#4CC9F0", width=2), opacity=1.0)
        fig_forecast.update_layout(template="plotly_dark", xaxis_title="Date", yaxis_title="Predicted Close")
        st.plotly_chart(fig_forecast, use_container_width=True)

        # Optional: prediction interval band
        if {"YHAT_LOWER", "YHAT_UPPER"}.issubset(df_forecast.columns):
            band = go.Figure()
            band.add_trace(go.Scatter(
                x=df_forecast["DS"], y=df_forecast["YHAT_UPPER"],
                line=dict(color="rgba(76,201,240,0)"),
                showlegend=False, hoverinfo="skip"
            ))
            band.add_trace(go.Scatter(
                x=df_forecast["DS"], y=df_forecast["YHAT_LOWER"],
                fill="tonexty", fillcolor="rgba(76,201,240,0.15)",
                line=dict(color="rgba(76,201,240,0)"),
                name="Forecast band"
            ))
            band.add_trace(go.Scatter(
                x=df_forecast["DS"], y=df_forecast["YHAT"],
                line=dict(color="#4CC9F0", width=2),
                name="Forecast"
            ))
            band.update_layout(template="plotly_dark", xaxis_title="Date", yaxis_title="Predicted Close")
            st.plotly_chart(band, use_container_width=True)
