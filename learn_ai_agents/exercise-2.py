"""
Exercise 2: The Reasoning Loop (ReAct)
Topic: Thought -> Action -> Observation -> Final Answer

In Exercise 1, we used simple 'if/else'. 
In real AI agents, we use a "Reasoning Loop". 
The agent doesn't just jump to an answer; it follows a cycle:
1. THOUGHT: The agent thinks about what it needs to do.
2. ACTION: The agent chooses a tool to call.
3. OBSERVATION: The agent 'sees' the output of the tool.
4. FINAL ANSWER: The agent provides the result to the user.
"""

import time

# --- TOOLS ---
def get_stock_price(ticker):
    """Simulates a stock market tool."""
    stocks = {"AAPL": "$150", "GOOGL": "$2800", "TSLA": "$700"}
    print(f"  [Tool] Searching stock database for {ticker}...")
    return stocks.get(ticker.upper(), "Unknown ticker")

def get_company_news(company):
    """Simulates a news search tool."""
    news = {
        "Apple": "Apple announces new iPhone 15.",
        "Google": "Google releases new AI model.",
        "Tesla": "Tesla opens new Gigafactory."
    }
    print(f"  [Tool] Searching news archives for {company}...")
    return news.get(company, "No recent news found.")

# --- THE AGENT ---
class ReasoningAgent:
    def __init__(self):
        self.tools = {
            "get_stock_price": get_stock_price,
            "get_company_news": get_company_news
        }

    def run(self, user_query):
        print(f"\nUser Request: {user_query}")
        
        # --- STEP 1: THOUGHT ---
        print("\nStep 1: THOUGHT")
        print("Agent: The user wants to know about Apple's stock and news. "
              "I first need to get the stock price for 'AAPL', then find news for 'Apple'.")
        time.sleep(1)

        # --- STEP 2: ACTION (Tool 1) ---
        print("\nStep 2: ACTION [Calling get_stock_price]")
        stock_result = self.tools["get_stock_price"]("AAPL")
        
        # --- STEP 3: OBSERVATION ---
        print(f"\nStep 3: OBSERVATION")
        print(f"Agent: I see the stock price is {stock_result}.")
        time.sleep(1)

        # --- STEP 4: THOUGHT (Again) ---
        print("\nStep 4: THOUGHT")
        print("Agent: Now that I have the stock, I need to get the latest news.")
        
        # --- STEP 5: ACTION (Tool 2) ---
        print("\nStep 5: ACTION [Calling get_company_news]")
        news_result = self.tools["get_company_news"]("Apple")

        # --- STEP 6: FINAL ANSWER ---
        print("\nStep 6: FINAL ANSWER")
        final_answer = (f"Apple (AAPL) is currently trading at {stock_result}. "
                        f"The latest news: {news_result}")
        print(f"Agent Response: {final_answer}")

# --- MAIN ---
if __name__ == "__main__":
    agent = ReasoningAgent()
    
    # We are simulating a multi-step task
    agent.run("How is Apple doing today? Give me their stock and latest news.")
