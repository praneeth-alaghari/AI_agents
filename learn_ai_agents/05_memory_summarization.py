"""
Exercise 5: The Efficient Banking Agent (Memory Compression)
Topic: Managing Long-Term Conversations in a Banking Context

This combines Exercise 4's Banking Tools with Exercise 5's Memory Summarization.
The goal is to prevent a banking session from becoming too 'expensive' while
still remembering the user's ID and previous actions.
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- TOOLS (From Exercise 4) ---
def get_user_balance(user_id):
    """Check the balance of a specific user ID."""
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

# --- THE EFFICIENT AGENT ---
class EfficientBankingAgent:
    def __init__(self, max_history=6):
        self.max_history = max_history
        self.summary = "The conversation has just started. No user ID or transaction history yet."
        self.history = [] # This stores the 'Sliding Window'
        self.system_prompt = "You are a secure banking assistant. Be helpful but brief."

    def summarize_history(self):
        """Asks the LLM to compress the oldest part of the conversation into a summary."""
        print("\n[System] >>> Memory buffer full! Compressing history into a summary...")
        
        # We turn the history into a string for the summarizer
        history_text = ""
        for msg in self.history:
            role = msg.get("role")
            content = msg.get("content", "[Action/Tool Result]")
            history_text += f"{role}: {content}\n"

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Condense this banking session into a short summary. Retain the User ID, any mentioned balances, and the User's current intent."},
                {"role": "user", "content": history_text}
            ]
        )
        
        self.summary = response.choices[0].message.content
        # We clear the history but keep the last 2 messages for immediate context flow
        self.history = self.history[-2:]
        print(f"[System] >>> New Summary: {self.summary}\n")

    def chat(self, user_input):
        # 1. Check if history needs compression
        if len(self.history) > self.max_history:
            self.summarize_history()

        # 2. Add current user input to sliding history
        self.history.append({"role": "user", "content": user_input})

        # 3. Construct the prompt with the SUMMARY
        messages_to_send = [
            {"role": "system", "content": f"{self.system_prompt}\n\nSUMMARY OF PREVIOUS CONTEXT: {self.summary}"}
        ]
        messages_to_send.extend(self.history)

        # 4. First Call to LLM
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages_to_send,
            tools=tools
        )
        
        response_msg = response.choices[0].message
        tool_calls = response_msg.tool_calls

        # Handle Tool Calls
        if tool_calls:
            self.history.append(response_msg) # Add tool intent to history
            
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                print(f"  [Agent Action] Calling tool: {function_name}{args}")
                
                result = tools_registry[function_name](**args)
                
                tool_msg = {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": str(result),
                }
                self.history.append(tool_msg)
            
            # Re-build messages for second call (including tool results)
            messages_to_send = [
                {"role": "system", "content": f"{self.system_prompt}\n\nSUMMARY OF PREVIOUS CONTEXT: {self.summary}"}
            ]
            messages_to_send.extend(self.history)

            second_response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages_to_send
            )
            final_content = second_response.choices[0].message.content
        else:
            final_content = response_msg.content

        # 5. Save the final answer to history
        self.history.append({"role": "assistant", "content": final_content})
        return final_content

if __name__ == "__main__":
    agent = EfficientBankingAgent(max_history=6)
    print("--- EFFICIENT BANKING AGENT STARTED ---")
    
    while True:
        txt = input("\nYou: ")
        if txt.lower() in ["exit", "quit"]: break
        print(f"Agent: {agent.chat(txt)}")
