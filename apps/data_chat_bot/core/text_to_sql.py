"""
Text-to-SQL conversion module.
Uses OpenAI to convert natural language questions into PostgreSQL queries
and then summarises the results back into natural language.
"""
import json
from openai import OpenAI
from core.config import settings
from core.database import get_table_schema, get_date_range, execute_raw_sql


_client = OpenAI(api_key=settings.OPENAI_API_KEY)


def _chat(messages: list[dict], model: str | None = None) -> str:
    """Low-level OpenAI chat completion helper."""
    response = _client.chat.completions.create(
        model=model or settings.OPENAI_MODEL,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content


def _date_serializer(obj):
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    return str(obj)


# ─── Public API ─────────────────────────────────────────────────────────────

def nl_to_sql(question: str, db_name: str, table_name: str) -> str:
    """
    Convert a natural-language question into a SQL query string.
    Returns either a raw SQL string or "NO_SQL: <response>" for non-data questions.
    """
    schema = get_table_schema(db_name, table_name)
    date_ctx = get_date_range(db_name, table_name) or "No date columns detected."

    system_prompt = f"""You are a SQL expert. Convert the user's natural language question into a PostgreSQL query for the following schema:

{schema}

Data Context:
{date_ctx}

Rules:
1. If the user input is a greeting (e.g., "Hi", "Hello") or a question NOT related to the data (e.g. "Who are you?"), return "NO_SQL: <Your conversational response>".
2. Otherwise, return ONLY the SQL query.
3. Do not wrap it in markdown or code blocks.
4. Use the table name 'public."{table_name}"'.
5. IMPORTANT: All column names may be mixed case. You MUST wrap ALL column names in double quotes.
6. If the user does not specify a year, use the year(s) found in the Data Context.
"""

    response = _chat([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ])

    if "NO_SQL:" in response:
        return response.strip()

    return response.strip().replace("```sql", "").replace("```", "").strip()


def run_query(sql: str, db_name: str) -> dict | str:
    """Execute a generated SQL query and return results."""
    if sql.startswith("NO_SQL:"):
        return sql.replace("NO_SQL:", "").strip()
    return execute_raw_sql(db_name, sql)


def summarise(question: str, sql: str, results, db_name: str, table_name: str) -> str:
    """Produce a natural-language summary of the query results."""
    if isinstance(results, str):
        return results

    results_str = json.dumps(results, default=_date_serializer, indent=2)

    system_prompt = (
        "You are a helpful data analyst. A specific SQL query was run to answer a "
        "user's question. Summarize the answer based on the data returned."
    )
    content = f"""
User Question: {question}
SQL Query Used: {sql}
Data Retrieved: {results_str}

Provide a clear, concise natural language answer. If the data is empty, state that no results were found.
If the data is tabular, feel free to format it as a markdown table for readability.
"""

    return _chat([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content},
    ])


def chat_with_data(question: str, db_name: str, table_name: str) -> dict:
    """
    End-to-end pipeline: question → SQL → execute → summarise.
    Returns a dict with keys: sql, raw_results, summary
    """
    sql = nl_to_sql(question, db_name, table_name)
    raw_results = run_query(sql, db_name)
    summary = summarise(question, sql, raw_results, db_name, table_name)

    return {
        "sql": sql if not sql.startswith("NO_SQL:") else None,
        "raw_results": raw_results if not isinstance(raw_results, str) else None,
        "summary": summary,
    }
