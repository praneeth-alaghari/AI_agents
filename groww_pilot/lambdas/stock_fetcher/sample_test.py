import requests
import xml.etree.ElementTree as ET

def fetch_nse_announcements():
    print("Hello world")

if __name__ == "__main__":
    news_items = fetch_nse_announcements()
    if news_items:
        print("Latest 10 NSE Announcements:")
        for item in news_items:
            print(f"- {item['title']} ({item['pub_date']}) [{item['link']}]")
    else:
        print("No news found or RSS feed not available.")