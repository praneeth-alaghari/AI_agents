import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

"""
Exercise 10: Structured Outputs (JSON Mode & Pydantic)
Topic: Forcing the LLM to return reliable JSON data, not just text.

Why?
If you want to plug an AI agent into another software system (like a database or API),
you can't just have it say "Sure, the user wants a refund."
You need: {"intent": "refund", "confidence": 0.98}

In this exercise, we will build a "Data Extraction Agent" that reads messy emails 
and converts them into clean JSON entries for a database.

We will use OpenAI's `response_format={"type": "json_object"}` to guarantee valid JSON.
"""

# =========================================================
# DATA: MESSY EMAILS FROM USERS
# =========================================================

EMAILS = [
    """
    Hi, I'm waiting for my order #5849. It's been 3 weeks! 
    I am very frustrated. I want my money back immediately.
    - John Doe
    """,
    """
    Hello team, just wanted to say check out the new feature, it works great! 
    Can I upgrade to the pro plan? 
    Thanks, Sarah.
    """,
    """
    My app keeps crashing when I upload a PNG file. Fix it.
    """
]

# =========================================================
# SYSTEM PROMPT WITH SCHEMA DEFINITION
# =========================================================

# We define the schema strictly in the prompt so the model knows EXACTLY what to output.
SCHEMA = """
{
    "customer_name": "string (or 'Unknown')",
    "order_id": "string (or null)",
    "sentiment": "string (positive, neutral, negative)",
    "urgency": "integer (1-5, where 5 is highest)",
    "category": "string (refund_request, technical_issue, general_inquiry, feedback)",
    "summary": "string (max 10 words)"
}
"""

SYSTEM_PROMPT = f"""
You are a Data Extraction Agent. 
Your job is to read customer emails and converting them into structured JSON data.

You MUST output valid JSON only. Do not add any markdown formatting like ```json.
Adhere strictly to this schema:
{SCHEMA}
"""

# =========================================================
# AGENT FUNCTION
# =========================================================

def extract_metadata(email_content):
    print("\n--- [Agent] Analyzing Email... ---")
    print(f"Content: {email_content.strip()[:50]}...") # Show snippet

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": email_content}
            ],
            response_format={"type": "json_object"} # <--- MAGIC KEY: Forces JSON output
        )

        # Parse the string content into a real Python dictionary
        data = json.loads(response.choices[0].message.content)
        return data

    except Exception as e:
        print(f"Error: {e}")
        return None

# =========================================================
# MAIN LOOP
# =========================================================

if __name__ == "__main__":
    print("Welcome to the Data Extraction Agent.")
    print("We will process 3 raw emails into a database-ready format.\n")

    database = []

    for email in EMAILS:
        structured_data = extract_metadata(email)
        
        if structured_data:
            print("  [Result] Successfully extracted:")
            print(json.dumps(structured_data, indent=2))
            database.append(structured_data)
        else:
            print("  [Result] Failed to extract.")

    print("\n--- FINAL DATABASE ---")
    print(f"Total records: {len(database)}")
    # In a real app, you would now doing: `db.insert(database)`
