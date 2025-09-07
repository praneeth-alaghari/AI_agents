import streamlit as st
import pandas as pd
import os
from lambdas.stock_fetcher.stock_list import STOCK_NAMES, STOCK_TICKER_MAP
import yfinance as yf

st.title("🚀 Groww Pilot Dashboardd")
st.subheader("Stock Price Viewer (Last 5 Days)")

tab1, tab2 = st.tabs(["Stock Prices", "Other Features"])

with tab1:
    st.write("Select a stock to view its last 5 days closing prices:")
    col1, col2 = st.columns([1, 3])
    with col1:
        selected_stock = st.radio("Stocks:", STOCK_NAMES)
    with col2:
        ticker = STOCK_TICKER_MAP.get(selected_stock)
        if ticker:
            @st.cache_data(show_spinner=True)
            def fetch_stock_data(ticker):
                data = yf.download(ticker, period="5d", interval="1d")
                if not data.empty:
                    return data[['Close']].reset_index()
                return pd.DataFrame()
            chart_df = fetch_stock_data(ticker)
            if not chart_df.empty:
                chart_df.columns = ["Date", "Close"]
                chart_df["Date"] = chart_df["Date"].dt.strftime('%Y-%m-%d')
                import altair as alt
                chart = alt.Chart(chart_df).mark_line(point=True).encode(
                    x=alt.X('Date', title='Date', axis=alt.Axis(labelAngle=-45)),
                    y=alt.Y('Close', title='Close Price', scale=alt.Scale(zero=False)),
                    tooltip=['Date', 'Close']
                ).properties(title=f"{selected_stock} - Last 5 Days")
                st.altair_chart(chart, use_container_width=True)
            else:
                st.warning("No data found for this stock.")
        else:
            st.warning("No ticker found for this stock.")

with tab2:
    st.write("Other features coming soon!")