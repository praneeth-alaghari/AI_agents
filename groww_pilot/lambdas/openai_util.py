import openai
from infra.openai_secrets import OPENAI_API_KEY

    # Replace with your OpenAI API key
    # Replace with your OpenAI API key


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
