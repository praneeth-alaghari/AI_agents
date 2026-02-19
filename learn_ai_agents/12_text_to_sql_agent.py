import json
import os
import urllib.parse
from sqlalchemy import create_engine, text
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv() # Loads from .env in the current directory

# Initialize OpenAI Client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    # Manual fallback for redundancy if needed, or error out
    print("Warning: OPENAI_API_KEY not found in environment variables.")

client = OpenAI(api_key=api_key)

def get_db_engine():
    # 1. Load secrets
    # Best Practice: Use environment variables or a git-ignored secrets file
    # We are using a git-ignored JSON file here for simplicity
    secrets_path = os.path.join(os.path.dirname(__file__), "secrets", "db_config.json")
    
    if os.path.exists(secrets_path):
        with open(secrets_path, "r") as f:
            config = json.load(f)
    else:
        # Fallback to environment variables if file doesn't exist (e.g. in production)
        config = {
            "DB_USER": os.getenv("DB_USER"),
            "DB_PASSWORD": os.getenv("DB_PASSWORD"),
            "DB_HOST": os.getenv("DB_HOST"),
            "DB_PORT": os.getenv("DB_PORT", "5432"),
            "DB_NAME": os.getenv("DB_NAME", "postgres"),
        }

    # 2. Create connection string
    # Format: postgresql://USER:PASSWORD@HOST:PORT/DB_NAME
    # We must URL-encode the password because it contains special characters (like '@')
    encoded_password = urllib.parse.quote_plus(config['DB_PASSWORD'])
    
    db_url = f"postgresql://{config['DB_USER']}:{encoded_password}@{config['DB_HOST']}:{config['DB_PORT']}/{config['DB_NAME']}"

    # 3. Create engine
    engine = create_engine(db_url)
    return engine

def date_serializer(obj):
    """JSON serializer for objects not serializable by default json code"""
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    return str(obj)

def get_chat_completion(messages, model="gpt-4o"):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling OpenAI: {e}"

def get_date_range():
    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            # We must quote "SaleDate" because of mixed-case/case-sensitivity policies we've seen
            query = text('SELECT MIN("SaleDate"), MAX("SaleDate") FROM public.product_sales_test;')
            result = conn.execute(query)
            min_date, max_date = result.fetchone()
            return f"The sales data ranges from {min_date} to {max_date}."
    except Exception as e:
        return f"Could not fetch date range: {e}"

def text_to_sql(user_question):
    print(f"\n[Agent]: Generating SQL for: '{user_question}'...")
    
    # 1. Fetch Context dynamically (RAG-lite)
    date_context = get_date_range()
    print(f"[Agent Context]: {date_context}")

    # Schema definition
    schema = """
    Table: product_sales_test
    Columns:
    - "ProductID" (text)
    - "ProductName" (text)
    - "Category" (text)
    - "Price" (double precision)
    - "QuantitySold" (bigint)
    - "SaleDate" (timestamp)
    """
    
    system_prompt = f"""You are a SQL expert. Convert the user's natural language question into a PostgreSQL query for the following schema:
    {schema}
    
    Data Context:
    {date_context}
    
    Rules:
    1. If the user input is a greeting (e.g., "Hi", "Hello") or specific question NOT related to data (e.g. "Who are you?"), return "NO_SQL: <Your conversational response>".
    2. Otherwise, return ONLY the SQL query.
    3. Do not wrap it in markdown or code blocks. 
    4. Use the table name 'public.product_sales_test'.
    5. IMPORTANT: All column names are mixed case. You MUST wrap ALL column names in double quotes (e.g., "ProductID", "SaleDate").
    6. If the user does not specify a year, use the year(s) found in the Data Context.
    """
    
    response = get_chat_completion([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_question}
    ])
    
    # Clean up response just in case
    # If it's a NO_SQL response, keep it as is (but strip whitespace)
    if "NO_SQL:" in response:
        return response.strip()

    sql_query = response.strip().replace("```sql", "").replace("```", "").strip()
    return sql_query

def execute_sql(query):
    # Check for NO_SQL flag
    if query.startswith("NO_SQL:"):
        return query.replace("NO_SQL:", "").strip()

    print(f"[Agent]: Executing SQL: {query}")
    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            result = conn.execute(text(query))
            if result.returns_rows:
                # Convert to list of dicts for easier processing
                columns = result.keys()
                # Row mapping to dict
                rows = [dict(zip(columns, row)) for row in result.fetchall()]
                return rows
            else:
                return "Query executed successfully (no rows returned)."
    except Exception as e:
        return f"Error executing SQL: {e}"

def summarize_results(question, sql_query, results):
    # If results is just a string (conversational response), return it directly
    if isinstance(results, str) and not results.startswith("Query executed") and not results.startswith("Error"):
        return results

    print(f"[Agent]: Summarizing results...")
    
    # Convert results to JSON string for the LLM
    results_str = json.dumps(results, default=date_serializer, indent=2)
    
    system_prompt = "You are a helpful data analyst. specific SQL query was run to answer a user's question. Summarize the answer based on the data returned."
    
    content = f"""
    User Question: {question}
    SQL Query Used: {sql_query}
    Data Retrieved: {results_str}
    
    Provide a clear, concise natural language answer. If the data is empty, state that no results were found.
    """
    
    return get_chat_completion([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content}
    ])

def chat_with_data():
    print("--- Text-to-SQL Agent Initialized ---")
    print("Ask questions about your 'product_sales_test' table (type 'exit' to quit).")
    
    while True:
        try:
            user_input = input("\nUser: ")
            if user_input.lower() in ["exit", "quit"]:
                break
                
            # 1. Generate SQL
            sql_query = text_to_sql(user_input)
            
            # 2. Execute SQL
            results = execute_sql(sql_query)
            
            # Check for execution errors
            if isinstance(results, str) and results.startswith("Error"):
                print(f"❌ {results}")
                continue
                
            # 3. Summarize Results
            summary = summarize_results(user_input, sql_query, results)
            
            print(f"\n[Agent]: {summary}")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    chat_with_data()
