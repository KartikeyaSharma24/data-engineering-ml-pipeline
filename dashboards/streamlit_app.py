# dashboards/streamlit_app.py

import streamlit as st
import pandas as pd
import plotly.express as px
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

# 4) Cached helpers (NO connection parameter!)
@st.cache_data(ttl=600)
def list_symbols() -> list[str]:
    sql = "SELECT DISTINCT SYMBOL FROM STOCK_FORECAST ORDER BY SYMBOL"
    cur = conn.cursor()
    cur.execute(sql)
    symbols = [row[0] for row in cur.fetchall()]
    cur.close()
    return symbols



@st.cache_data(ttl=600)
def load_forecast(symbol: str) -> pd.DataFrame:
    sql = """
        SELECT 
            TRY_TO_DATE(DS) AS DS,
            TRY_TO_DOUBLE(YHAT) AS YHAT,
            SYMBOL
        FROM STOCK_FORECAST
        WHERE SYMBOL = %(symbol)s
        ORDER BY DS
    """
    cur = conn.cursor()
    cur.execute(sql, {"symbol": symbol})
    rows = cur.fetchall()
    cur.close()
    df = pd.DataFrame(rows, columns=["DS", "YHAT", "SYMBOL"])
    df["DS"] = pd.to_datetime(df["DS"], errors="coerce")
    df["YHAT"] = pd.to_numeric(df["YHAT"], errors="coerce")
    df = df.dropna(subset=["DS", "YHAT"])
    return df

@st.cache_data(ttl=600)
def load_actuals(symbol: str) -> pd.DataFrame:
    sql = """
        SELECT 
            TRY_TO_DATE(DS) AS DS,
            TRY_TO_DOUBLE(CLOSE) AS CLOSE,
            SYMBOL
        FROM STOCK_ACTUALS
        WHERE SYMBOL = %(symbol)s
        ORDER BY DS
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


# 5) Sidebar — select from actual symbols present in Snowflake
symbols = list_symbols()
if not symbols:
    st.error("No symbols found in STOCK_FORECAST. Verify your pipeline loaded data.")
    st.stop()

symbol = st.sidebar.selectbox("Symbol", options=symbols, index=0)

# 6) Layout & charts
st.header("📈 Stocks — Actuals & Forecast")
col1, col2 = st.columns(2)

# Actuals panel
with col1:
    st.subheader(f"Actual Close — {symbol}")
    try:
        df_actuals = load_actuals(symbol)
        st.caption(f"Actual rows: {len(df_actuals)}")
        if df_actuals.empty:
            st.warning(f"No actuals found for '{symbol}'.")
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
    except Exception as e:
        st.exception(e)

# Forecast panel
with col2:
    st.subheader(f"Forecast — {symbol}")
    try:
        df_forecast = load_forecast(symbol)

        # Instrumentation to debug blank charts
        st.caption(f"Forecast rows: {len(df_forecast)}")
        st.write("Sample forecast rows:", df_forecast.head(5))
        st.write("Dtypes:", df_forecast.dtypes.to_dict())
        st.write("NaN counts:", df_forecast.isna().sum().to_dict())

        if df_forecast.empty or df_forecast["YHAT"].isna().all():
            st.warning(f"No forecast data (or all NaNs) for '{symbol}'. Try another symbol or check pipeline.")
        else:
            fig_forecast = px.line(
                df_forecast,
                x="DS",
                y="YHAT",
                title=f"Forecast — {symbol}",
            )
            # Ensure visible line on dark theme
            fig_forecast.update_traces(line=dict(color="#4CC9F0", width=2), opacity=1.0)
            fig_forecast.update_layout(template="plotly_dark", xaxis_title="Date", yaxis_title="Predicted Close")
            st.plotly_chart(fig_forecast, use_container_width=True)
    except Exception as e:
        st.exception(e)

# 7) (Optional) No explicit conn.close(); cache_resource will keep it for the session
