import pandas as pd
import snowflake.connector
import streamlit as st

st.set_page_config(page_title="Stocks Forecast", layout="wide")
st.title("📈 Stocks — Actuals & Forecast")

SF = st.secrets["snowflake"]  # Secrets will be set in Streamlit Cloud

@st.cache_data(ttl=300)
def load_data():
    conn = snowflake.connector.connect(
        user=SF["user"], password=SF["password"], account=SF["account"],
        warehouse=SF["warehouse"], database=SF["database"], schema=SF["schema"]
    )
    cur = conn.cursor()

    cur.execute("SELECT DISTINCT SYMBOL FROM V_STOCK_SILVER ORDER BY SYMBOL")
    symbols = [r[0] for r in cur.fetchall()]

    cur.execute("SELECT SYMBOL, DT, CLOSE, VOLUME, RET_PCT FROM V_STOCK_SILVER")
    silver = pd.DataFrame(cur.fetchall(), columns=["SYMBOL","DT","CLOSE","VOLUME","RET_PCT"])

    cur.execute("SELECT SYMBOL, DS, YHAT, YHAT_LOWER, YHAT_UPPER FROM V_STOCK_FORECAST")
    forecast = pd.DataFrame(cur.fetchall(), columns=["SYMBOL","DS","YHAT","YHAT_LOWER","YHAT_UPPER"])

    cur.close(); conn.close()
    return symbols, silver, forecast

symbols, df_silver, df_forecast = load_data()
symbol = st.sidebar.selectbox("Symbol", symbols)

left, right = st.columns(2)

s_actual = df_silver[df_silver["SYMBOL"] == symbol].sort_values("DT")
s_fore   = df_forecast[df_forecast["SYMBOL"] == symbol].sort_values("DS")

with left:
    st.subheader(f"Actual Close — {symbol}")
    st.line_chart(s_actual.set_index("DT")["CLOSE"])

with right:
    st.subheader(f"Forecast — {symbol}")
    st.line_chart(s_fore.set_index("DS")[["YHAT","YHAT_LOWER","YHAT_UPPER"]])

st.caption("Pipeline: Databricks (ETL/ML) → Snowflake (storage) → Streamlit (viz)")
