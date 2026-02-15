
import json

# =========================================================
# 1. WHY DO WE NEED json.loads()?
# =========================================================

# The OpenAI API returns a *String*, not a Python Dictionary.
# setting response_format={"type": "json_object"} just guarantees 
# that the String is formatted correctly (valid JSON syntax).

# Simulation of what OpenAI returns:
openai_response_string = '{\n  "ticket_id": "TICKET-123",\n  "priority": "high",\n  "action": "escalate_to_manager"\n}'

print("--- TYPE CHECK ---")
print(f"Type from OpenAI: {type(openai_response_string)}") 
# Output: <class 'str'>

# You CANNOT do this with a string:
# if openai_response_string["priority"] == "high":  <-- CRASH! TypeError

# You MUST parse it first:
data = json.loads(openai_response_string)
print(f"Type after json.loads(): {type(data)}") 
# Output: <class 'dict'>

# Now you can use it in logic:
if data["priority"] == "high":
    print("✅ Logic Check: This is a high priority ticket.")


# =========================================================
# 2. REAL WORLD USE CASE: AUTOMATION PIPELINE
# =========================================================

# Imagine we extracted this from a chaotic customer email:
structured_data = [
    {
        "customer": "Angry Alice",
        "category": "refund",
        "urgency": 5,
        "amount": 50.00
    },
    {
        "customer": "Happy Bob", 
        "category": "feedback",
        "urgency": 1,
        "amount": 0
    }
]

print("\n--- REAL WORLD PIPELINE EXECUTION ---")

def process_ticket(ticket):
    # 1. ROUTING LOGIC (The "Why we need JSON")
    # Because it's a dict, we can write code against it:
    
    if ticket["category"] == "refund":
        if ticket["urgency"] >= 4:
            # Automatic Refund via Stripe API (Mock)
            print(f"💸 [Finance API] Auto-refunding ${ticket['amount']} to {ticket['customer']} (Reason: High Urgency)")
        else:
            # Manual Review
            print(f"👀 [Dashboard] Flagging refund for {ticket['customer']} for manual review.")
            
    elif ticket["category"] == "feedback":
        # Save to Product Roadmap Database
        print(f"💾 [Database] Saving feedback from {ticket['customer']} to 'Product Ideas' table.")

    elif ticket["category"] == "tech_support":
        # Create JIRA Ticket
        print(f"🐞 [Jira API] Creating bug report for {ticket['customer']}.")

# Process them
for item in structured_data:
    process_ticket(item)
