"""
Exercise 3: The Real AI Agent (LLM + Tools)
Topic: Function Calling and Dynamic Reasoning

Now we are using a real "Brain" (OpenAI's LLM). 
Instead of 'if/else', the LLM will decide which tool to use 
based on the descriptions we give it.
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# 1. Load credentials from .env
load_dotenv() 
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- TOOLS ---
# These are the functions the AI can actually 'run'
def get_weather(location):
    """Get the current weather for a specific city."""
    # Simulation
    weather_data = {"london": "Foggy, 12°C", "dubai": "Sunny, 35°C", "new york": "Cloudy, 20°C"}
    
    location_lower = location.lower()
    for city, status in weather_data.items():
        if city in location_lower:
            return status
            
    return "Weather unavailable for this city."

def calculate_investment(amount, interest_rate, years):
    """Calculate the future value of an investment."""
    future_value = amount * (1 + interest_rate/100) ** years
    return f"${future_value:,.2f}"

# --- DEFINING TOOLS FOR THE LLM ---
# This is how we tell the LLM what our tools do
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "The city and state, e.g. San Francisco, CA"},
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_investment",
            "description": "Calculate how much money you will have in the future",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number", "description": "Starting amount"},
                    "interest_rate": {"type": "number", "description": "Yearly interest rate (%)"},
                    "years": {"type": "integer", "description": "Number of years"},
                },
                "required": ["amount", "interest_rate", "years"],
            },
        },
    }
]

# --- TOOL REGISTRY ---
# This maps the library of functions to their names. 
# No matter how many tools we add, we just add them to this dictionary!
tools_registry = {
    "get_weather": get_weather,
    "calculate_investment": calculate_investment,
}

def run_agent(query):
    print(f"\n[User]: {query}")
    
    messages = [{"role": "user", "content": query}]
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        print(f"\n[Agent Thought]: I need to use {len(tool_calls)} tool(s) to answer this.")
        
        # 1. Add the assistant's request to call tools to the history
        messages.append(response_message)
        
        # 2. Execute ALL requested tools
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            print(f"[Agent Action]: Dynamically calling tool '{function_name}' with {args}")
            
            if function_name in tools_registry:
                result = tools_registry[function_name](**args)
            else:
                result = f"Error: Tool {function_name} not found."
            
            print(f"[Agent Observation]: Tool '{function_name}' returned: {result}")
            
            # 3. Add EACH tool result to the history
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": str(result),
            })
        
        # 4. Call the LLM one LAST time to get the final combined answer
        second_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        
        print(f"\n[Agent Final Answer]: {second_response.choices[0].message.content}")

    else:
        # If no tool was needed
        print(f"\n[Agent Final Answer]: {response_message.content}")

if __name__ == "__main__":
    print("--- STARTING REAL AI AGENT ---")
    
    # Testing multiple tool calls at once
    run_agent("What is the weather of Dubai and London?")
