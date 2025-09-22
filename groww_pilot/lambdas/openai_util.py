import openai
from infra.openai_secrets import OPENAI_API_KEY


def get_openai_response(prompt):
    # Replace with your OpenAI API key
    openai.api_key = OPENAI_API_KEY

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return str(e)
