
# Groww Pilot

AI-powered stock portfolio assistant built with Streamlit and AWS EC2.  

🚀 **[Click Here for Demo](http://52.66.142.248:8501)**  


# Groww Pilot

A Python project for stock price analysis using yfinance.

## Structure

- `src/` - Python scripts and modules
- `data/` - Datasets and CSV files
- `notebooks/` - Jupyter notebooks
- `tests/` - Unit tests


## Features

- `tests/__init__.py`: This is the initializer for the tests package, suggesting that any submodules or test scripts in this directory are utilized for testing purposes.
- `streamlit_app/` - Streamlit application files
  - `streamlit_app/__init__.py`: This file initializes the Streamlit app package, allowing for the organization of related modules.
  - `streamlit_app/ui_fragments.py`: Contains utility functions that return HTML/CSS code snippets. These functions create a scrollable list for the UI, enhancing layouts for enhanced user experience.
  - `streamlit_app/app.py`: This is the main Streamlit application code. It sets up the UI for the Groww Pilot Dashboard, enabling users to interact with stock prices, view recent news, and use an AI chat feature powered by OpenAI. Key functionalities include:
    - Tabs for displaying stock prices and news.
    - A radio button for stock selection.
    - Integration with the Yahoo Finance API for fetching stock prices.
    - Displaying latest news from the NSE RSS feed and Marketaux API.
    - A chat section for user interaction with an AI chatbot.
- `infra/` - Infrastructure-related files
  - `infra/marketaux_token.py`: This file contains the API token for accessing the Marketaux API, which is used to fetch financial news.
  - `infra/__init__.py`: An initializer for the infrastructure package, indicating organization of modules related to infrastructure.
- `lambdas/` - Serverless functions
  - `lambdas/__init__.py`: Initializes the lambdas package, suggesting that the scripts in this directory are intended to be serverless functions.
  - `lambdas/writer_dynamo/app.py`: This file serves as the entry point for the DynamoDB writer lambda function, likely for saving data to a DynamoDB database.
  - `lambdas/sentiment/app.py`: Entry point for the sentiment analysis lambda function, suggesting that it processes data to extract sentiment related to stocks.
  - `lambdas/stock_fetcher/` - Stock fetching functionalities
    - `lambdas/stock_fetcher/__init__.py`: Initializes the stock fetcher package, allowing the organization of modules for fetching stock data.
    - `lambdas/stock_fetcher/stock_list.py`: Contains two lists: `STOCK_NAMES`, a collection of names of stocks for fetching, and `STOCK_TICKER_MAP`, a mapping of stock names to their corresponding ticker symbols for data retrieval.
    - `lambdas/stock_fetcher/sample_test.py`: A sample script that tests the OpenAI API key functionality. It makes a test request to confirm if the OpenAI GPT model is working correctly.

Overall, the project is structured to provide a comprehensive dashboard for tracking stock prices, receiving market news, and leveraging AI chat capabilities for user interaction and assistance.

