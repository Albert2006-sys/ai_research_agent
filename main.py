from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import google.generativeai as genai
from typing import List, Optional
import datetime
import uuid

# Firebase Admin SDK for database interaction
import firebase_admin
from firebase_admin import credentials, firestore

# --- Your Existing Logic ---
from newspaper import Article
from serpapi import GoogleSearch

# --- SETUP ---
load_dotenv()
try:
    # Initialize Firebase
    cred = credentials.Certificate("firebase-credentials.json")
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()

    # Initialize Generative AI
    google_api_key = os.getenv("GOOGLE_API_KEY")
    serpapi_api_key = os.getenv("SERPAPI_API_KEY")
    if not google_api_key or not serpapi_api_key:
        raise ValueError("API keys must be set.")
    genai.configure(api_key=google_api_key)
except Exception as e:
    print(f"CRITICAL: Failed to initialize services: {e}")

# --- Pydantic Data Models ---
class Source(BaseModel):
    title: str
    url: str
    publish_date: Optional[str] = None
    authors: List[str] = []

class Message(BaseModel):
    id: str
    role: str  # "user" or "model"
    content: str
    sources: Optional[List[Source]] = None

class Conversation(BaseModel):
    id: str
    title: str
    messages: List[Message]
    createdAt: str

class ConversationMeta(BaseModel):
    id: str
    title: str

# --- FastAPI App ---
app = FastAPI(title="Perplexity-Style AI Research API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# --- Helper Functions ---
def search_the_web(query: str) -> List[str]:
    print(f"Searching for: {query}...")
    try:
        params = {"q": query, "api_key": serpapi_api_key, "num": 5, "engine": "google"}
        search = GoogleSearch(params)
        results = search.get_dict()
        urls = [result['link'] for result in results.get('organic_results', [])]
        return urls
    except Exception as e:
        print(f"Error during web search: {e}")
        return []

def scrape_and_process_urls(urls: List[str]) -> (str, List[Source]):
    print("Scraping URLs...")
    combined_content = ""
    sources_data = []
    for url in urls:
        try:
            article = Article(url)
            article.download()
            article.parse()
            if article.text:
                combined_content += f"--- CONTENT FROM {url} ---\n{article.text}\n\n"
                sources_data.append(Source(
                    title=article.title,
                    url=url,
                    publish_date=str(article.publish_date) if article.publish_date else None,
                    authors=article.authors
                ))
        except Exception as e:
            print(f"Could not scrape {url}: {e}")
    return combined_content, sources_data

def summarize_content(content: str, query: str) -> str:
    print("Summarizing content with Google Gemini...")
    if not content:
        return "No content was scraped to summarize."
    prompt = f"""
    Based on the following web content, provide a clear and comprehensive answer to the user's query.
    Instructions:
    1. First, provide a direct, concise summary that immediately answers the user's question.
    2. Then, create a section with bullet points detailing the most important findings, facts, or key takeaways.
    3. Use Markdown for formatting (e.g., **bold**, *italics*, bullet points).
    USER QUERY: "{query}"
    COMBINED WEB CONTENT:\n{content}
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error during summarization: {e}")
        return "Failed to generate summary due to an AI model error."

# --- API ENDPOINTS ---
@app.get("/conversations", response_model=List[ConversationMeta])
async def get_all_conversations():
    """Retrieves metadata for all conversations."""
    try:
        # QUICK FIX: Removed the .order_by() clause to prevent the need for a Firestore index.
        # This gets the app working quickly. The list will not be sorted by date.
        convs_ref = db.collection('conversations').stream()
        convs_list = [{"id": conv.id, "title": conv.to_dict().get("title", "Untitled")} for conv in convs_ref]
        return convs_list
    except Exception as e:
        print(f"Error fetching conversations: {e}")
        raise HTTPException(status_code=500, detail="Could not fetch conversations from the database.")


@app.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str):
    """Retrieves a single, full conversation by its ID."""
    doc_ref = db.collection('conversations').document(conversation_id)
    doc = doc_ref.get()
    if doc.exists:
        return Conversation(**doc.to_dict())
    raise HTTPException(status_code=404, detail="Conversation not found.")

@app.post("/conversations", response_model=Conversation)
async def create_conversation(request: dict):
    """Starts a new research conversation."""
    query = request.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="Query is required.")

    # Perform the research
    urls = search_the_web(query)
    if not urls:
        raise HTTPException(status_code=404, detail="No relevant web sources found for that query.")
    
    content, sources = scrape_and_process_urls(urls)
    if not content:
        raise HTTPException(status_code=500, detail="Could not extract content from any of the web sources.")

    summary = summarize_content(content, query)

    # Create conversation structure
    convo_id = str(uuid.uuid4())
    user_message = Message(id=str(uuid.uuid4()), role="user", content=query)
    model_message = Message(id=str(uuid.uuid4()), role="model", content=summary, sources=sources)

    new_convo = Conversation(
        id=convo_id,
        title=query,
        messages=[user_message, model_message],
        createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat()
    )

    # Save to Firestore
    db.collection('conversations').document(convo_id).set(new_convo.dict())
    return new_convo

