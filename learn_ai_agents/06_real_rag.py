"""
Exercise 6: Real RAG (Semantic Search with Embeddings)
Topic: Moving beyond keywords to 'meaning' (Vector Search)

In 'Real' RAG:
1. We convert text into 'Embeddings' (long lists of numbers representing meaning).
2. We compare the 'distance' between the User's question and our documents.
3. This allows the agent to find 'wire transfers' even if the user says 'sending money abroad'.
"""

import os
import json
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- KNOWLEDGE BASE ---
# These are the 'chunks' of our knowledge base.
POLICIES = [
    "International wire transfers have a $35 fee and take 3-5 business days to process.",
    "The daily ATM withdrawal limit is $500 for Standard accounts and $2,000 for Gold accounts.",
    "Savings accounts earn a 4.2% APY interest rate, which is compounded on a monthly basis.",
    "Fraud protection policy: Report unauthorized transactions within 48 hours for 100% liability protection.",
    "To open a new checking account, you need a valid government ID and a minimum deposit of $25.",
    "Overdraft protection is available for a $10 fee per occurrence, capped at 3 times per day."
]

# --- EMBEDDING ENGINE ---
# We turn our policies into vectors (lists of numbers) just once.
print("--- [System] Indexing Knowledge Base (Creating Embeddings)... ---")

def get_embedding(text, model="text-embedding-3-small"):
    return client.embeddings.create(input=[text], model=model).data[0].embedding

# Store the vectors for all policies
POLICY_VECTORS = [get_embedding(p) for p in POLICIES]

def cosine_similarity(v1, v2):
    """Calculates how 'close' two vectors are in meaning."""
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

# --- TOOLS ---
def semantic_search_policy(query: str):
    """Uses Vector Math to find the most relevant bank policy."""
    print(f"  [Real RAG] Semantically searching for: '{query}'...")
    
    # 1. Get embedding for the user's query
    query_vector = get_embedding(query)
    
    # 2. Compare query vector to all policy vectors
    similarities = [cosine_similarity(query_vector, pv) for pv in POLICY_VECTORS]
    
    # 3. Find the index of the highest similarity
    best_index = np.argmax(similarities)
    best_score = similarities[best_index]
    
    print(f"  [Real RAG] Highest match score: {best_score:.4f}")
    
    if best_score > 0.4: # Only return if it's reasonably related
        return POLICIES[best_index]
    
    return "No relevant bank policy found."

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
    },
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

tools_registry = {
    "get_user_balance": get_user_balance,
    "semantic_search_policy": semantic_search_policy
}

# --- THE AGENT ---
class RealRagAgent:
    def __init__(self):
        self.memory = [{"role": "system", "content": "You are a helpful bank assistant. Always use the search tool if the user asks about rules or fees."}]

    def chat(self, user_input):
        self.memory.append({"role": "user", "content": user_input})
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=self.memory,
            tools=tools
        )
        
        msg = response.choices[0].message
        if msg.tool_calls:
            self.memory.append(msg)
            for tool_call in msg.tool_calls:
                fn_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                result = tools_registry[fn_name](**args)
                
                self.memory.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": fn_name,
                    "content": str(result),
                })
            
            second_response = client.chat.completions.create(model="gpt-4o", messages=self.memory)
            final_ans = second_response.choices[0].message.content
        else:
            final_ans = msg.content

        self.memory.append({"role": "assistant", "content": final_ans})
        return final_ans

# --- MAIN ---
if __name__ == "__main__":
    agent = RealRagAgent()
    print("\n--- REAL RAG AGENT READY ---")
    
    while True:
        txt = input("\nYou: ")
        if txt.lower() in ["exit", "quit"]: break
        print(f"Agent: {agent.chat(txt)}")
