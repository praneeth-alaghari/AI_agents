from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
from tools.call_weather import get_weather
from tools.call_weather_forecast import get_forecast_open_meteo
from tools.call_personal_weather_prefs import search_weather_knowledge
import os
from collections import deque
from langchain_core.tools import tool



load_dotenv()


llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)


tools = [get_weather, get_forecast_open_meteo, search_weather_knowledge]
agent_executor = create_react_agent(llm, tools)


# System prompt to guide agent behavior
SYSTEM_PROMPT = """You are a helpful weather assistant.

Use your weather tools to fetch current weather data and forecasts when needed.

For everything else, use your general knowledge to help the user - especially when they ask follow-up questions about weather information you've already shared.

Be conversational and helpful. Use the conversation history to understand context.

1. Once weather data is fetched, always check user's personal weather preferences via search_weather_knowledge tool.
2. Based on the fetched weather data and the user's preferences, provide personalized advice on clothing, activities, health tips, and food recommendations."""


class ConversationHistory:
    """Manages conversation history with a maximum size limit"""
    
    def __init__(self, max_conversations=5):
        """
        Args:
            max_conversations: Maximum number of conversation pairs to keep
        """
        self.max_conversations = max_conversations
        # Using deque for efficient FIFO operations
        self.history = deque(maxlen=max_conversations * 2)  # *2 for user+AI messages
    
    def add_message(self, role, content):
        """Add a message to history
        
        Args:
            role: 'human' or 'ai'
            content: The message content
        """
        if role == 'human':
            self.history.append(HumanMessage(content=content))
        elif role == 'ai':
            self.history.append(AIMessage(content=content))
    
    def get_messages(self):
        """Get all messages in history"""
        return list(self.history)
    
    def clear(self):
        """Clear all history"""
        self.history.clear()
    
    def get_summary(self):
        """Get a human-readable summary of conversation history"""
        if not self.history:
            return "No conversation history"
        
        summary = []
        for i, msg in enumerate(self.history):
            if isinstance(msg, HumanMessage):
                summary.append(f"User: {msg.content}")
            elif isinstance(msg, AIMessage):
                summary.append(f"Agent: {msg.content[:100]}...")
        return "\n".join(summary)


if __name__ == "__main__":
    print("🌤️  Weather Agent with Live Reasoning & Memory\n")
    print("Watch the agent think and use tools in real-time!")
    print("The agent remembers your last 5 conversations.\n")
    print("Commands:")
    print("  - 'exit' or 'quit': Exit the program")
    print("  - 'history': View conversation history")
    print("  - 'clear': Clear conversation history\n")
    
    # Initialize conversation history
    conversation_memory = ConversationHistory(max_conversations=5)
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ["exit", "quit"]:
            print("\nGoodbye! 👋")
            break
        
        if user_input.lower() == "history":
            print("\n📚 CONVERSATION HISTORY")
            print("="*60)
            print(conversation_memory.get_summary())
            print("="*60 + "\n")
            continue
        
        if user_input.lower() == "clear":
            conversation_memory.clear()
            print("\n🗑️  Conversation history cleared!\n")
            continue
        
        if not user_input:
            continue
        
        try:
            final_response = None
            
            # Build message list with system prompt + history + current message
            messages = [SystemMessage(content=SYSTEM_PROMPT)]
            messages.extend(conversation_memory.get_messages())
            messages.append(HumanMessage(content=user_input))
            
            # Stream the agent's execution in real-time with system prompt and history
            for chunk in agent_executor.stream(
                {"messages": messages},
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
                
                # Add both user input and AI response to history
                conversation_memory.add_message('human', user_input)
                conversation_memory.add_message('ai', final_response)
            else:
                print("Agent: (No response generated)\n")
                
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
