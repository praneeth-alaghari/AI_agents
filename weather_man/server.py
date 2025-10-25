import requests
import json
import os
from openai import OpenAI

# Replace with your OpenAI API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MCP_WEATHER_URL = "https://abcd1234xyz.execute-api.ap-south-1.amazonaws.com/weather"

# Memory to remember past queries
memory = []

def call_weather_mcp(city: str) -> str:
    """Call the MCP server dynamically"""
    try:
        resp = requests.get(MCP_WEATHER_URL, params={"city": city})
        if resp.status_code == 200:
            return resp.json()["weather"]
        else:
            return "I couldn't fetch the weather."
    except Exception:
        return "Error contacting the weather service."

def agent_respond(user_input: str) -> str:
    """Main agent loop: use LLM to parse intent and call MCP dynamically"""
    
    # Build the prompt for LLM
    messages = [
        {"role": "system", "content": 
         "You are an AI agent. When the user asks about the weather, "
         "return a JSON object with keys 'tool':'weather' and 'city':'city_name'. "
         "Otherwise, respond normally."},
        {"role": "user", "content": user_input}
    ]
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0
    )
    
    output_text = response.choices[0].message.content.strip()
    
    # Try to parse JSON
    try:
        data = json.loads(output_text)
        if data.get("tool") == "weather" and "city" in data:
            city = data["city"]
            weather = call_weather_mcp(city)
            reply = f"The weather in {city} is {weather}."
        else:
            reply = output_text
    except Exception:
        # If LLM didn't return JSON, just reply normally
        reply = output_text
    
    # Save memory
    memory.append({"user_input": user_input, "ai_response": reply})
    return reply

# ------------------------
# Run the Agent
# ------------------------
if __name__ == "__main__":
    print("AI Agent (type 'exit' to quit)")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        reply = agent_respond(user_input)
        print("AI:", reply)
