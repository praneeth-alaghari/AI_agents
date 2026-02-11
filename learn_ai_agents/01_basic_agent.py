"""
Exercise 1: Introduction to AI Agents
Topic: The Basic Components of an Agent

An AI Agent is more than just a function. It is a system that:
1. PERCEIVES its environment (receives input).
2. REASONS about the situation (decides what to do).
3. ACTS to achieve a goal (executes a task).
"""

import time

# --- TOOLS (Actions the agent can take) ---
def get_weather(city):
    """A mock tool to simulate fetching weather data."""
    # In a real agent, this would call an API.
    weather_data = {
        "london": "15°C and Cloudy",
        "new york": "22°C and Sunny",
        "tokyo": "18°C and Rainy"
    }
    return weather_data.get(city.lower(), "Weather data not found.")

def get_time():
    """A tool to simulate fetching current time."""
    return time.strftime("%H:%M:%S")

# --- THE AGENT ---
class SimpleAgent:
    def __init__(self, name):
        self.name = name

    def process_request(self, user_input):
        print(f"\n[{self.name}] Thinking...")
        time.sleep(1) # Simulating thinking time
        
        # 1. PERCEPTION: Analyzing the string
        input_text = user_input.lower()

        # 2. REASONING: Simple if-else (The 'Brain')
        # In advanced agents, this would be an LLM (like GPT-4 or Claude).
        if "weather" in input_text:
            # Extract city (simplistic logic)
            if "london" in input_text: city = "london"
            elif "tokyo" in input_text: city = "tokyo"
            else: city = "new york"
            
            # 3. ACTION: Calling the weather tool
            result = get_weather(city)
            return f"I checked the weather for {city.capitalize()}: {result}"

        elif "time" in input_text:
            # 3. ACTION: Calling the time tool
            result = get_time()
            return f"The current time is {result}"

        else:
            return "I'm sorry, I only know about weather and time right now!"

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # Create our agent instance
    my_agent = SimpleAgent(name="AssistantBot")

    print(f"Hello! I am {my_agent.name}. How can I help you today?")
    
    # Simulate a few interactions
    queries = [
        "What is the weather in London?",
        "Tell me the current time",
        "Can you play some music?"
    ]

    for query in queries:
        print(f"\nUser: {query}")
        response = my_agent.process_request(query)
        print(f"Agent: {response}")
