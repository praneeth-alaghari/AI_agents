
import yfinance as yf

# Fetch Reliance stock data (NSE: RELIANCE.NS)
ticker = yf.Ticker("RELIANCE.NS")
print(dir(ticker))
data = ticker.history(period="1d")

# Print current price
current_price = data['Close'].iloc[-1]
print(f"Reliance currensdt stock price: {current_price}")
