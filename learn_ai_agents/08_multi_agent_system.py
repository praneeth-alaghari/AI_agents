"""
Exercise 8: Multi-Agent Systems (The Triage Pattern)
Topic: Routing requests to specialized agents for better reliability.

In this exercise:
1. We create a 'Triage Agent' (The Receptionist).
2. We create two specialized agents: 'Policy Expert' and 'Account Manager'.
3. The Triage agent decides who should handle the user's request.


Single agent -> sequential flow of what needs to be called next
Single agent + Tools -> LLM decides what tool to select and sequence of tools
Multi agent routing type -> LLM decides which agent it should choose and that agent choose its own tools (single agent + tools). these give data/analysis individually(not feedback loop)
Hierarchical Multi-Agent -> LLM decides which agent it should choose and each agent passes analysis/suggestions but finally gives back to router and router(boss) merge all outputs to give a final answer (there is one boss agent)
Fully Decentralized multi agent -> LLM decides which agents it should choose. there is no boss Each agent fight with each other until they agree to a point
"""

import os
import json
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =========================================================
# MOCK VAULT + UTILITIES
# =========================================================

POLICIES = [
    "Wire transfer fee is $15 for domestic and $45 for international transfers.",
    "ATM withdrawal limit is $500 per day.",
    "Overdraft fee is $35 per occurrence."
]

def get_embedding(text, model="text-embedding-3-small"):
    return client.embeddings.create(input=[text], model=model).data[0].embedding

# Precompute embeddings once
POLICY_VECTORS = [get_embedding(p) for p in POLICIES]

def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def semantic_search_policy(query: str):
    print("[Tool] semantic_search_policy called...")
    query_vector = get_embedding(query)
    similarities = [cosine_similarity(query_vector, pv) for pv in POLICY_VECTORS]
    best_index = np.argmax(similarities)

    if similarities[best_index] > 0.4:
        return POLICIES[best_index]
    return "No relevant bank policy found."

def get_user_balance(user_id: str):
    print("[Tool] get_user_balance called...")
    balances = {"user_123": "$1,250.00", "user_456": "$50.00"}
    return balances.get(user_id, "User not found.")

# =========================================================
# TOOL DEFINITIONS
# =========================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "semantic_search_policy",
            "description": "Search bank policies",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_balance",
            "description": "Check user balance",
            "parameters": {
                "type": "object",
                "properties": {"user_id": {"type": "string"}},
                "required": ["user_id"]
            }
        }
    }
]

# =========================================================
# EXECUTE TOOL
# =========================================================

def execute_tool(name, args):
    if name == "semantic_search_policy":
        return semantic_search_policy(**args)
    elif name == "get_user_balance":
        return get_user_balance(**args)

# =========================================================
# 1️⃣ SINGLE AGENT (NO TOOLS)
# =========================================================

def single_agent(question):
    print("\n[Single Agent] Thinking...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": question}]
    )
    return response.choices[0].message.content

# =========================================================
# 2️⃣ SINGLE AGENT WITH TOOLS
# =========================================================

def single_agent_with_tools(question):
    print("\n[Single Agent + Tools] Thinking...")

    messages = [
        {"role": "system", "content": "You are a bank assistant."},
        {"role": "user", "content": question}
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=TOOLS
    )

    msg = response.choices[0].message

    if msg.tool_calls:
        for tool_call in msg.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            print(f"[Single Agent] Calling tool: {name}")
            result = execute_tool(name, args)

            messages.append(msg)
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": name,
                "content": str(result)
            })

        final = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        return final.choices[0].message.content

    return msg.content

# =========================================================
# 3️⃣ MULTI AGENT (ROUTING / TRIAGE)
# =========================================================

def triage_route(question):
    print("\n[Triage Agent] Deciding routing...")
    if "fee" in question.lower():
        print("[Triage] Routing to Policy Expert")
        return semantic_search_policy(question)
    elif "balance" in question.lower():
        print("[Triage] Routing to Account Manager")
        return get_user_balance("user_123")
    else:
        return "General query."

# =========================================================
# 4️⃣ HIERARCHICAL MULTI AGENT
# =========================================================

def hierarchical_system(question):
    print("\n[Manager Agent] Decomposing problem...")

    print("[Manager] Delegating policy part...")
    policy = semantic_search_policy(question)

    print("[Manager] Delegating account part...")
    balance = get_user_balance("user_123")

    print("[Manager] Combining responses...")
    return f"{policy}\n\nAccount Balance: {balance}"

# =========================================================
# 5️⃣ FULLY DECENTRALIZED
# =========================================================

def decentralized_system(question):
    print("\n[Policy Agent] Independently analyzing...")
    policy = semantic_search_policy(question)

    print("[Account Agent] Independently analyzing...")
    balance = get_user_balance("user_123")

    print("[Consensus Layer] Merging peer outputs...")
    return f"{policy}\n\nAccount Balance: {balance}"

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    question = "What is the wire transfer fee and also tell me the balance for user_123?"

    print("\n===== AGENT ARCHITECTURE DEMO =====")
    print("1. Single Agent")
    print("2. Single Agent with Tools")
    print("3. Multi Agent (Routing)")
    print("4. Hierarchical Multi Agent")
    print("5. Fully Decentralized Multi Agent")

    choice = input("\nSelect (1-5): ")

    if choice == "1":
        answer = single_agent(question)
    elif choice == "2":
        answer = single_agent_with_tools(question)
    elif choice == "3":
        answer = triage_route(question)
    elif choice == "4":
        answer = hierarchical_system(question)
    elif choice == "5":
        answer = decentralized_system(question)
    else:
        print("Invalid choice.")
        exit()

    print("\n===== FINAL ANSWER =====")
    print(answer)
