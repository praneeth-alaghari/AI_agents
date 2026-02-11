"""
Exercise 4: The Stateful Agent (Memory & Chat History)
Topic: Maintaining Context and Short-Term Memory

In previous exercises, the agent forgot everything once the request was over.
In this exercise, we introduce a 'Memory' (Conversation History).
The LLM will now 'remember' previous parts of the conversation.
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# 1. Setup
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- TOOLS ---
def get_user_balance(user_id):
    """Get the current balance of a user's wallet."""
    # Simulation: Imagine this connects to a Database
    balances = {"user_123": "$1,250.00", "user_456": "$50.00"}
    return balances.get(user_id, "User not found.")

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_user_balance",
            "description": "Check the balance of a specific user ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "The ID of the user, e.g. user_123"},
                },
                "required": ["user_id"],
            },
        },
    }
]

tools_registry = {"get_user_balance": get_user_balance}

# --- THE AGENT WITH MEMORY ---
class StatefulAgent:
    def __init__(self):
        # This list is the "Memory" of the agent.
        # It stores every message from both the User and the Assistant.
        self.memory = [
            {"role": "system", "content": "You are a helpful banking assistant. Be concise."}
        ]

    def chat(self, user_input):
        # 1. Add User's new message to memory
        self.memory.append({"role": "user", "content": user_input})
        
        # 2. Call LLM with the ENTIRE memory
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=self.memory,
            tools=tools
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        # Handle Tool Calls (If any)
        if tool_calls:
            # We must add the Assistant's intent to call tools to memory
            self.memory.append(response_message)

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                print(f"  [Agent] Calling tool: {function_name}({args})")
                result = tools_registry[function_name](**args)
                
                # Add tool result to memory
                self.memory.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": str(result),
                })
            
            # Get final response after tools
            second_response = client.chat.completions.create(
                model="gpt-4o",
                messages=self.memory,
            )
            final_content = second_response.choices[0].message.content
        else:
            final_content = response_message.content

        # 3. Add Assistant's final answer to memory
        self.memory.append({"role": "assistant", "content": final_content})
        return final_content

# --- INTERACTIVE CHAT LOOP ---
if __name__ == "__main__":
    agent = StatefulAgent()
    print("--- BANKING AGENT STARTED (Type 'exit' to quit) ---")
    print("Tip: Tell him your user_id first, then ask for your balance later.")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Agent: Goodbye!")
            break
            
        answer = agent.chat(user_input)
        print(f"Agent: {answer}")
