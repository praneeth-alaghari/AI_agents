from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores  import FAISS
from dotenv import load_dotenv
from langchain_core.tools import tool

import os

load_dotenv()

my_prefs = """
I Like cold weather and dislike hot weather. I prefer cloudy days over sunny days.
when its raining I like to stay indoors and read a book or watch movies.
I enjoy eating warm comfort foods like soup and stew during rainy weather.
I dislike humid weather as it makes me feel uncomfortable and sticky.
When its cold i catch cold easily"""


embeddings = OpenAIEmbeddings(
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

vector_store = FAISS.from_texts(
    texts=[my_prefs],
    embedding=embeddings
)

@tool
def search_weather_knowledge(query: str) -> str:
    """Search weather knowledge base for helpful information about my personalized prefereces on health,weather, clothing, food, and activities."""
    
    # Search for the 2 most similar documents
    docs = vector_store.similarity_search(query, k=2)
    
    # Return them as text
    return "\n".join([doc.page_content for doc in docs])