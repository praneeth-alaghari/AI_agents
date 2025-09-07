import os
import google.generativeai as genai

def get_api_key():
    key = os.environ.get("GOOGLE_AI_API_KEY")
    if key:
        return key
    try:
        with open(os.path.join(os.path.dirname(__file__), '../../infra/google_ai_api_key.txt'), 'r') as f:
            return f.readline().strip()
    except Exception:
        return None

def get_gemini_model(api_key):
    genai.configure(api_key=api_key)
    models = [m.name for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
    if not models:
        print("No Gemini model available for content generation.")
        return None
    print(models)
    return 'models/gemini-1.5-flash'

def test_prompt(prompt):
    api_key = get_api_key()
    model_name = get_gemini_model(api_key)
    if not model_name:
        print("No model found.")
        return
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        print("Prompt:", prompt)
        print("Response:", response.text.strip())
    except Exception as e:
        print(f"Gemini SDK error: {e}")

if __name__ == "__main__":
    # Example prompt
    test_prompt("What is the capital of India?")
