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
    return 'models/gemini-2.5-flash'

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
    import time

    print("--- Gemini LLM RPM Test ---")
    print("RPM (Requests Per Minute) means the number of API calls you can make in any 60-second window. If your limit is 60 RPM, you can send 60 requests in 60 seconds, then must wait for the next window.")
    print("This script will send as many requests as possible in 60 seconds and report the count.")

    api_key = get_api_key()
    model_name = get_gemini_model(api_key)
    if not model_name:
        print("No model found.")
        exit(1)
    model = genai.GenerativeModel(model_name)

    start = time.time()
    end = start + 60
    count = 0
    errors = 0
    while time.time() < end:
        try:
            response = model.generate_content(f"Test prompt {count+1}")
            print("Response:", response.text.strip())
            count += 1
        except Exception as e:
            errors += 1
            print(f"Error at request {count+1}: {e}")
            time.sleep(1)  # Wait a bit if error (rate limit, etc.)
    print(f"Total successful requests in 1 minute: {count}")
    print(f"Total errors: {errors}")
