import requests
from infra.google_secrets import API_KEY, CX

def google_custom_search(query):
    url = f'https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={CX}&q={query}'
    response = requests.get(url)
    
    if response.status_code == 200:
        
        data = response.json()
        results = []
        for item in data.get("items", []):
            title = item.get("title")
            snippet = item.get("snippet")
            link = item.get("link")
            results.append(f"{title} - {snippet} (Source: {link})")

        context = "\n".join(results)

        return context
    else:
        return None
