from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage
from dotenv import load_dotenv
from tools.call_weather import get_weather
from tools.call_weather_forecast import get_forecast_open_meteo
import os

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

tools = [get_weather, get_forecast_open_meteo]
agent_executor = create_react_agent(llm, tools)

# System prompt to guide agent behavior
SYSTEM_PROMPT = """You are a helpful weather assistant with access to specific weather tools.

⚠️ IMPORTANT RULES:
1. ONLY use your tools when the user asks about WEATHER-related information (temperature, conditions, rain, forecast, etc.)
2. For non-weather queries, politely answer using your general knowledge and explain what you cannot help with
3. Don't force-fit weather tools to unrelated questions

DO Not let user know that you are confined to weather tools only.
"""

if __name__ == "__main__":
    print("🌤️  Weather Agent with Live Reasoning\n")
    print("Watch the agent think and use tools in real-time!\n")
    print("Type 'exit' to quit\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ["exit", "quit"]:
            print("\nGoodbye! 👋")
            break
        
        if not user_input:
            continue
        
        print("\n" + "="*60)
        print("🧠 AGENT THINKING PROCESS (LIVE)")
        print("="*60 + "\n")
        
        try:
            final_response = None
            
            # Stream the agent's execution in real-time with system prompt
            for chunk in agent_executor.stream(
                {
                    "messages": [
                        SystemMessage(content=SYSTEM_PROMPT),
                        ("human", user_input)
                    ]
                },
                stream_mode="updates"
            ):
                for node_name, updates in chunk.items():
                    if "messages" in updates:
                        for msg in updates["messages"]:
                            
                            # 1. Show when agent decides to call a tool
                            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                                for tool_call in msg.tool_calls:
                                    print(f"🔧 Agent Decision: Call tool '{tool_call['name']}'")
                                    print(f"   📥 Input: {tool_call['args']}")
                                    print()
                            
                            # 2. Show tool execution results
                            elif hasattr(msg, 'name') and msg.name:
                                print(f"✅ Tool '{msg.name}' executed successfully")
                                # Show truncated result
                                result_preview = msg.content[:150].replace('\n', ' ')
                                if len(msg.content) > 150:
                                    result_preview += "..."
                                print(f"   📤 Output: {result_preview}")
                                print()
                            
                            # 3. Show final AI response
                            elif hasattr(msg, 'type') and msg.type == 'ai' and msg.content:
                                final_response = msg.content
            
            # Display final answer
            print("="*60)
            print("💬 FINAL RESPONSE")
            print("="*60 + "\n")
            
            if final_response:
                print(f"Agent: {final_response}\n")
            else:
                print("Agent: (No response generated)\n")
                
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
