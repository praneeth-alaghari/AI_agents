from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import pandas as pd
import os
from lambdas.stock_fetcher.stock_list import STOCK_NAMES, STOCK_TICKER_MAP
import yfinance as yf
from streamlit_app.ui_fragments import get_scrollbar_css, get_scrollable_radio_start, get_scrollable_radio_end

st.set_page_config(layout="wide")

st.title("🚀 Groww Pilot Dashboardd")
st.subheader("Stock Price Viewer (Tabs + Scrollable List)")

# Inject custom CSS for scrollable radio list
st.markdown(get_scrollbar_css(), unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Stock Prices", "Other Features"])

with tab1:
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(get_scrollable_radio_start(), unsafe_allow_html=True)
        selected_stock = st.radio("Stocks:", STOCK_NAMES, key="stock_radio")
        st.markdown(get_scrollable_radio_end(), unsafe_allow_html=True)
    with col2:
        inner_tab1, inner_tab2 = st.tabs(["Last 5 COBs", "Latest News"])
        with inner_tab1:
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
        with inner_tab2:
            st.write(f"### Latest News for {selected_stock} (via Marketaux)")
            import importlib.util
            token_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'infra', 'marketaux_token.py')
            spec = importlib.util.spec_from_file_location("marketaux_token", token_path)
            marketaux_token = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(marketaux_token)
            api_token = marketaux_token.MARKETAUX_API_TOKEN

            def fetch_stock_marketaux_news(stock_name):
                # Try to get ticker symbol from STOCK_TICKER_MAP
                ticker = STOCK_TICKER_MAP.get(stock_name)
                url = "https://api.marketaux.com/v1/news/all"
                params = {
                    "api_token": api_token,
                    "language": "en",
                    "limit": 10,
                    "countries": "in"
                }
                if ticker:
                    params["symbols"] = ticker
                else:
                    params["search"] = stock_name
                try:
                    response = requests.get(url, params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json().get("data", [])
                        news_items = []
                        for item in data:
                            title = item.get("title", "No Title")
                            url_ = item.get("url", "#")
                            desc = item.get("description", "")
                            date = item.get("published_at", "")
                            news_items .append({"Headline": f"[{title}]({url_})", "Description": desc, "Date": date})
                        return news_items
                    else:
                        return []
                except Exception as e:
                    return []

            stock_news = fetch_stock_marketaux_news(selected_stock)

                if stock_news:
                    df_stock_news = pd.DataFrame(stock_news)
                    st.write("#### News Table")
                    st.markdown("Click headlines to open links.")
                    st.write(df_stock_news.to_markdown(index=False), unsafe_allow_html=True)
                else:
                    st.info(f"No Marketaux news found for {selected_stock} or API error.")

            # --- Streamlit Native Chatbot ---
            st.write("---")
            st.write("### Portfolio Stock Chatbot (Streamlit Native)")
            if "chat_history" not in st.session_state:
                st.session_state["chat_history"] = []

            user_input = st.chat_input("Ask about any portfolio stock...")
            if user_input:
                # Dummy response logic, replace with LLM or custom logic
                response = f"You asked: {user_input}. (This is a placeholder response. Integrate LLM for real answers.)"
                st.session_state["chat_history"].append(("user", user_input))
                st.session_state["chat_history"].append(("bot", response))

            for role, msg in st.session_state["chat_history"]:
                st.chat_message(role).write(msg)

            # --- Floating External Chatbot Widget ---
            st.markdown(
                '''
                <style>
                .chatbot-float {
                    position: fixed;
                    bottom: 24px;
                    right: 24px;
                    z-index: 9999;
                    width: 350px;
                    height: 500px;
                    border: none;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                    border-radius: 12px;
                    overflow: hidden;
                }
                </style>
                <iframe class="chatbot-float" src="https://www.chatbase.co/chatbot-iframe/YOUR_CHATBOT_ID" allow="clipboard-write;" frameborder="0"></iframe>
                ''', unsafe_allow_html=True
            )

with tab2:
    st.write("### Latest 10 News Headlines (NSE RSS Feed)")
    import requests
    import xml.etree.ElementTree as ET
    @st.cache_data(show_spinner=True)
    def fetch_nse_announcements():
        url = "https://nsearchives.nseindia.com/content/RSS/Online_announcements.xml"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        news_items = []
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            for item in root.findall(".//item")[:10]:
                title = item.find("title").text if item.find("title") is not None else "No Title"
                link = item.find("link").text if item.find("link") is not None else "#"
                pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
                description = item.find("description").text if item.find("description") is not None else ""
                news_items.append({"Headline": f"[{title}]({link})", "Description": description, "Date": pub_date})
        return news_items
    news_items = fetch_nse_announcements()
    if news_items:
        df = pd.DataFrame(news_items)
        st.write("#### News Table")
        st.markdown("Click headlines to open links.")
        st.write(df.to_markdown(index=False), unsafe_allow_html=True)
    else:
        st.info("No news found or RSS feed not available.")

    # Marketaux API Feed
    st.write("### Marketaux News Feed (Global Finance & Market News)")
    import importlib.util
    token_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'infra', 'marketaux_token.py')
    spec = importlib.util.spec_from_file_location("marketaux_token", token_path)
    marketaux_token = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(marketaux_token)
    api_token = marketaux_token.MARKETAUX_API_TOKEN

    def fetch_marketaux_news():
        url = "https://api.marketaux.com/v1/news/all"
        params = {
            "api_token": api_token,
            "language": "en",
            "limit": 10,
            "countries": "in"
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json().get("data", [])
                news_items = []
                for item in data:
                    title = item.get("title", "No Title")
                    url_ = item.get("url", "#")
                    desc = item.get("description", "")
                    date = item.get("published_at", "")
                    news_items.append({"Headline": f"[{title}]({url_})", "Description": desc, "Date": date})
                return news_items
            else:
                return []
        except Exception as e:
            return []

    marketaux_news = fetch_marketaux_news()
    if marketaux_news:
        df_mx = pd.DataFrame(marketaux_news)
        st.write("#### Marketaux News Table")
        st.markdown("Click headlines to open links.")
        st.write(df_mx.to_markdown(index=False), unsafe_allow_html=True)
    else:
        st.info("No Marketaux news found or API error.")