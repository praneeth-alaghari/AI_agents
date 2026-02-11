"""
Exercise 7: Persistent Knowledge (Vector Storage)
Topic: Saving Embeddings so we don't re-calculate every time.

In this exercise:
1. We save our Embeddings to a local JSON file ('bank_vault.json').
2. When the script starts, it check if 'bank_vault.json' exists.
3. If yes, it loads it (Instant!). If no, it creates it.
"""

import os
import json
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

VAULT_FILE = "bank_vault.json"

POLICIES = [
    "International wire transfers have a $35 fee and take 3-5 business days to process.",
    "The daily ATM withdrawal limit is $500 for Standard accounts and $2,000 for Gold accounts.",
    "Savings accounts earn a 4.2% APY interest rate, which is compounded on a monthly basis.",
    "Fraud protection policy: Report unauthorized transactions within 48 hours for 100% liability protection.",
    "To open a new checking account, you need a valid government ID and a minimum deposit of $25.",
    "Overdraft protection is available for a $10 fee per occurrence, capped at 3 times per day."
]

def get_embedding(text, model="text-embedding-3-small"):
    return client.embeddings.create(input=[text], model=model).data[0].embedding

def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

# --- PERSISTENCE LOGIC ---
def load_or_create_vault():
    if os.path.exists(VAULT_FILE):
        print(f"--- [System] Loading existing Knowledge Base from '{VAULT_FILE}'... ---")
        with open(VAULT_FILE, "r") as f:
            data = json.load(f)
            return data["vectors"], data["policies"]
    else:
        print("--- [System] No vault found. Creating new Knowledge Base (Indexing)... ---")
        vectors = [get_embedding(p) for p in POLICIES]
        
        # Save to disk
        vault_data = {"vectors": vectors, "policies": POLICIES}
        with open(VAULT_FILE, "w") as f:
            json.dump(vault_data, f)
            
        print(f"--- [System] Knowledge Base saved to '{VAULT_FILE}'! ---")
        return vectors, POLICIES

# Load the vault once at startup
POLICY_VECTORS, SAVED_POLICIES = load_or_create_vault()

# --- TOOLS ---
def semantic_search_policy(query: str):
    """Uses the saved vectors to find the most relevant bank policy."""
    print(f"  [Vault Search] Querying disk for: '{query}'...")
    query_vector = get_embedding(query)
    similarities = [cosine_similarity(query_vector, pv) for pv in POLICY_VECTORS]
    best_index = np.argmax(similarities)
    
    if similarities[best_index] > 0.4:
        return SAVED_POLICIES[best_index]
    return "No relevant bank policy found."

# (Rest of the agent logic remains the same)
tools = [
    {
        "type": "function",
        "function": {
            "name": "semantic_search_policy",
            "description": "Look up bank policies regarding fees, limits, and rules",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The topic to search for"},
                },
                "required": ["query"],
            },
        },
    }
]

tools_registry = {"semantic_search_policy": semantic_search_policy}

class PersistentRagAgent:
    def __init__(self):
        self.memory = [{"role": "system", "content": "You are a helpful bank assistant."}]

    def chat(self, user_input):
        self.memory.append({"role": "user", "content": user_input})
        response = client.chat.completions.create(model="gpt-4o", messages=self.memory, tools=tools)
        msg = response.choices[0].message
        
        if msg.tool_calls:
            self.memory.append(msg)
            for tool_call in msg.tool_calls:
                fn_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                result = tools_registry[fn_name](**args)
                self.memory.append({"tool_call_id": tool_call.id, "role": "tool", "name": fn_name, "content": str(result)})
            
            second_response = client.chat.completions.create(model="gpt-4o", messages=self.memory)
            final_ans = second_response.choices[0].message.content
        else:
            final_ans = msg.content

        self.memory.append({"role": "assistant", "content": final_ans})
        return final_ans

if __name__ == "__main__":
    agent = PersistentRagAgent()
    print("\n--- PERSISTENT RAG AGENT READY ---")
    while True:
        txt = input("\nYou: ")
        if txt.lower() in ["exit", "quit"]: break
        print(f"Agent: {agent.chat(txt)}")
