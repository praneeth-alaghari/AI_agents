"""
Exercise 9: Human-in-the-Loop (Safety & Confirmation)
Topic: Pausing execution for user approval before sensitive actions.

In this exercise:
1. We have a 'sensitive' tool: `transfer_funds`.
2. The agent is autonomous for read-only actions (checking balances).
3. But for write actions (transfers), it STOPS and asks the Human (you) for permission.
4. If approved, it proceeds. If denied, it handles the rejection gracefully.

This pattern is CRITICAL for production agents to prevent accidental damage.
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =========================================================
# MOCK DATABASE & TOOLS
# =========================================================

SYSTEM_DB = {
    "user_123": {"balance": 1000},
    "user_456": {"balance": 500}
}

def get_balance(user_id: str):
    print(f"[Tool] Checking balance for {user_id}...")
    user = SYSTEM_DB.get(user_id)
    if user:
        return f"${user['balance']}"
    return "User not found."

def transfer_funds(from_user: str, to_user: str, amount: int):
    # In a real app, this would modify the database.
    # Here we just simulate it.
    print(f"[Tool] 💸 INITIATING TRANSFER: ${amount} from {from_user} to {to_user}...")
    
    if SYSTEM_DB[from_user]['balance'] >= amount:
        SYSTEM_DB[from_user]['balance'] -= amount
        SYSTEM_DB[to_user]['balance'] += amount
        return f"Transfer successful. New balance for {from_user}: ${SYSTEM_DB[from_user]['balance']}"
    else:
        return "Insufficient funds."

# Tool Definitions
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_balance",
            "description": "Check the balance of a user.",
            "parameters": {
                "type": "object",
                "properties": {"user_id": {"type": "string"}},
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "transfer_funds",
            "description": "Transfer money between users. REQUIRES APPROVAL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "from_user": {"type": "string"},
                    "to_user": {"type": "string"},
                    "amount": {"type": "integer"}
                },
                "required": ["from_user", "to_user", "amount"]
            }
        }
    }
]

# Map names to functions
TOOL_MAP = {
    "get_balance": get_balance,
    "transfer_funds": transfer_funds
}

# Define which tools require human (user) approval
SENSITIVE_TOOLS = ["transfer_funds"]

# =========================================================
# AGENT LOOP WITH HUMAN-IN-THE-LOOP
# =========================================================

def run_agent_with_approval(user_id, prompt):
    messages = [
        {"role": "system", "content": f"You are a helpful banking assistant for user {user_id}."},
        {"role": "user", "content": prompt}
    ]

    print(f"\n--- Processing Request: '{prompt}' ---")

    # Step 1: LLM decides what to do
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=TOOLS
    )
    
    msg = response.choices[0].message
    messages.append(msg) # Add agent's thought/tool_call to history

    # Step 2: Check for Tool Calls
    if msg.tool_calls:
        for tool_call in msg.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            print(f"[Agent] Wants to call: {name}({args})")

            # --- THE HUMAN-IN-THE-LOOP CHECK ---
            if name in SENSITIVE_TOOLS:
                print(f"\n⚠️  APPROVAL REQUIRED for {name}!")
                print(f"⚠️  Args: {args}")
                user_decision = input("👉 Approve this action? (y/n): ").strip().lower()

                if user_decision != "y":
                    print("❌ Action Denied by User.")
                    # We inject a "Tool Error" message so the agent knows it failed
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": name,
                        "content": "Error: User denied permission to execute this action."
                    })
                    continue # Skip execution, go to next loop (or next tool)

                print("✅ Action Approved.")
            
            # Execute the tool (either safe or approved)
            result = TOOL_MAP[name](**args)
            
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": name,
                "content": str(result)
            })

        # Step 3: Get Final Response after Tool Execution
        final_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        return final_response.choices[0].message.content

    return msg.content

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    print("Welcome to the Secure Bank Agent.")
    print("Commands: 'balance', 'transfer 100 to user_456', 'exit'")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            break
            
        response = run_agent_with_approval("user_123", user_input)
        print(f"Agent: {response}")
