import requests

API_KEY = "AIzaSyAZmSYldc-aBwlwCsm896jYlD8xwvkF7A4"
CX = "500f9cb6667f24b9e"
query = "python"

url = "https://www.googleapis.com/customsearch/v1"
params = {
    "key": API_KEY,
    "cx": CX,
    "q": 'news about Anant raj industries'
}

response = requests.get(url, params=params)
data = response.json()

# Print titles of first results
results = []
for item in data.get("items", []):
    title = item.get("title")
    snippet = item.get("snippet")
    link = item.get("link")
    results.append(f"{title} - {snippet} (Source: {link})")

context = "\n".join(results)

return context