import os
import google.generativeai as genai
import pandas as pd
import yfinance as yf

DEFAULT_MODEL = 'models/gemini-1.5-flash'
FALLBACK_MODEL = 'models/gemini-2.5-flash'

try:
    from .stock_list import STOCK_NAMES, STOCK_TICKER_MAP  # For package/module import
except ImportError:
    from stock_list import STOCK_NAMES, STOCK_TICKER_MAP  # For direct script execution

def get_api_key():
    key = os.environ.get("GOOGLE_AI_API_KEY")
    if key:
        return key
    try:
        with open(os.path.join(os.path.dirname(__file__), '../../infra/google_ai_api_key.txt'), 'r') as f:
            return f.readline().strip()
    except Exception:
        return None

def batch_llm_get_ticker_map(stock_names, api_key):
    genai.configure(api_key=api_key)
    model_name = DEFAULT_MODEL
    prompt = (
        "Convert the following Indian stock names to their Yahoo Finance ticker symbols for use with yfinance Python library. "
        "Return a JSON object mapping each stock name to its ticker symbol. Use the NSE (.NS) or BSE (.BO) suffix where possible. "
        "If the stock is an ETF or mutual fund, return the correct Yahoo Finance symbol.\n"
        f"Stock names: {stock_names}"
    )
    print(prompt)
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        import json as pyjson
        mapping = pyjson.loads(response.text)
        return mapping
    except Exception as e:
        if "quota" in str(e).lower():
            print(f"Quota error for {model_name}, trying fallback model {FALLBACK_MODEL}")
            try:
                model = genai.GenerativeModel(FALLBACK_MODEL)
                response = model.generate_content(prompt)
                import json as pyjson
                mapping = pyjson.loads(response.text)
                return mapping
            except Exception as e2:
                print(f"Gemini SDK error for batch ticker mapping (fallback): {e2}")
                return {}
        print(f"Gemini SDK error for batch ticker mapping: {e}")
        return {}

def llm_get_ticker(stock_name, api_key):
    genai.configure(api_key=api_key)
    model_name = DEFAULT_MODEL
    prompt = (
        f"Convert the following Indian stock name to its Yahoo Finance ticker symbol for use with yfinance Python library. "
        f"Return only the ticker symbol, and if possible, use the NSE (.NS) or BSE (.BO) suffix. "
        f"If the stock is an ETF or mutual fund, return the correct Yahoo Finance symbol. "
        f"Stock name: {stock_name}"
    )
    print(prompt)
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        ticker = response.text.strip()
        return ticker
    except Exception as e:
        if "quota" in str(e).lower():
            print(f"Quota error for {model_name}, trying fallback model {FALLBACK_MODEL}")
            try:
                model = genai.GenerativeModel(FALLBACK_MODEL)
                response = model.generate_content(prompt)
                ticker = response.text.strip()
                return ticker
            except Exception as e2:
                print(f"Gemini SDK error for {stock_name} (fallback): {e2}")
                return None
        print(f"Gemini SDK error for {stock_name}: {e}")
        return None

def fetch_last_5_days(stock_name, ticker):
    if not ticker:
        print(f"No valid ticker found for {stock_name}")
        return pd.DataFrame()
    try:
        data = yf.download(ticker, period="5d", interval="1d")
        if not data.empty:
            return data[['Close']]
        else:
            return pd.DataFrame()
    except Exception as e:
        print(f"Error fetching {stock_name}: {e}")
        return pd.DataFrame()

def update_ticker_map(new_map):
    import ast
    import re
    stock_list_path = os.path.join(os.path.dirname(__file__), 'stock_list.py')
    with open(stock_list_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Replace STOCK_TICKER_MAP definition
    new_map_str = "STOCK_TICKER_MAP = " + repr(new_map)
    content = re.sub(r'STOCK_TICKER_MAP\s*=\s*\{[^}]*\}', new_map_str, content, flags=re.DOTALL)
    with open(stock_list_path, 'w', encoding='utf-8') as f:
        f.write(content)

def fetch_all_stocks():
    api_key = get_api_key()
    # Use persistent ticker map first
    ticker_map = dict(STOCK_TICKER_MAP)
    missing_stocks = [s for s in STOCK_NAMES if s not in ticker_map or not ticker_map[s]]
    print(f"Missing tickers for {len(missing_stocks)} stocks.")
    if missing_stocks:
        batch_map = batch_llm_get_ticker_map(missing_stocks, api_key)
        ticker_map.update(batch_map)
        # Persistently update stock_list.py with new tickers
        update_ticker_map(ticker_map)
    result = {}
    for stock in STOCK_NAMES[:10]:
        ticker = ticker_map.get(stock)
        if not ticker:
            ticker = llm_get_ticker(stock, api_key)
            ticker_map[stock] = ticker
            update_ticker_map(ticker_map)
        result[stock] = fetch_last_5_days(stock, ticker)
    return result

if __name__ == "__main__":
    all_data = fetch_all_stocks()
    for stock, df in all_data.items():
        print(f"{stock}:")
        print(df)
