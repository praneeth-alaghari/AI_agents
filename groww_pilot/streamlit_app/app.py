from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import pandas as pd
import openai
from lambdas.openai_util import get_openai_response
from lambdas.stock_fetcher.stock_list import STOCK_NAMES, STOCK_TICKER_MAP
import yfinance as yf
from lambdas.google_custom_search import google_custom_search
from streamlit_app.ui_fragments import get_scrollbar_css, get_scrollable_radio_start, get_scrollable_radio_end
from infra.openai_secrets import OPENAI_API_KEY
from lambdas.chatbot import chatbot_interface
st.set_page_config(layout="wide")

st.title("🚀 Groww Pilot Dashboard")
st.subheader("Stock Price Viewer (Tabs + Scrollable List)")

st.markdown(get_scrollbar_css(), unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Stock Prices", "Other Features", "AI Chat"])

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
            st.write(f"### Latest News for {selected_stock} (Google Search)")
            context = google_custom_search(f'latest news for {selected_stock}')
            prompt = f"""
                    Here are some search results about '{selected_stock}':
                    {context}
                    Summarize the news into exactly 5 bullet points, clear and concise.
                    """
            llm_response = get_openai_response(prompt)
            st.write(llm_response)

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

    st.write("### Marketaux News Feed (Global Finance & Market News)")

with tab3:
    st.title("AI Chat using LangChain")
    st.subheader("Connect with OpenAI's chatbot")
    chatbot_interface()

