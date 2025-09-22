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

# Global variables to track service availability
db = None
google_api_key = None
serpapi_api_key = None
services_initialized = False

def initialize_services():
    """Initialize all external services (Firebase, Google AI, etc.)"""
    global db, google_api_key, serpapi_api_key, services_initialized
    
    missing_services = []
    
    # Initialize Firebase
    try:
        if not os.path.exists("firebase-credentials.json"):
            missing_services.append("Firebase credentials file (firebase-credentials.json)")
        else:
            cred = credentials.Certificate("firebase-credentials.json")
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
            db = firestore.client()
            print("✓ Firebase initialized successfully")
    except Exception as e:
        missing_services.append(f"Firebase (Error: {e})")

    # Initialize API keys
    google_api_key = os.getenv("GOOGLE_API_KEY")
    serpapi_api_key = os.getenv("SERPAPI_API_KEY")
    
    if not google_api_key:
        missing_services.append("GOOGLE_API_KEY environment variable")
    if not serpapi_api_key:
        missing_services.append("SERPAPI_API_KEY environment variable")
    
    # Initialize Generative AI if key is available
    if google_api_key:
        try:
            genai.configure(api_key=google_api_key)
            print("✓ Google Generative AI initialized successfully")
        except Exception as e:
            missing_services.append(f"Google Generative AI (Error: {e})")
    
    if missing_services:
        print("⚠️  WARNING: Some services could not be initialized:")
        for service in missing_services:
            print(f"   - {service}")
        print("\n📋 To fully configure the backend:")
        print("   1. Copy .env.example to .env and add your API keys")
        print("   2. Copy firebase-credentials.json.example to firebase-credentials.json and add your Firebase credentials")
        print("   3. Restart the backend")
        print("\n🚀 Backend is starting but some features may not work without proper configuration...\n")
    else:
        services_initialized = True
        print("✅ All services initialized successfully!")

# Initialize services on startup
initialize_services()

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
    if not serpapi_api_key:
        print("SerpAPI key not available - returning demo URLs")
        # Return some demo URLs for testing when API is not available
        return [
            "https://en.wikipedia.org/wiki/Main_Page",
            "https://www.example.com"
        ]
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
    
    # If no internet access or in demo mode, provide sample content
    if not serpapi_api_key and len(urls) <= 2:  # Demo URLs
        print("Demo mode: Using sample content")
        combined_content = """
        --- SAMPLE CONTENT FOR DEMO ---
        This is sample content that would normally be scraped from web sources.
        In a real environment with proper API keys and internet access, this would contain
        actual content from relevant web pages related to the user's query.
        
        The AI research agent would normally:
        1. Search the web using SerpAPI
        2. Scrape content from relevant pages
        3. Process and summarize the information
        4. Return a comprehensive response with sources
        """
        sources_data.append(Source(
            title="Demo Content",
            url="https://example.com/demo",
            publish_date=None,
            authors=["Demo Author"]
        ))
        return combined_content, sources_data
    
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
    
    if not google_api_key:
        return f"""**Demo Response for: "{query}"**

⚠️ This is a demo response as the Google API key is not configured.

Based on your query "{query}", here's what a typical response would look like:

**Key Points:**
- This is a placeholder response showing the expected format
- The actual response would contain relevant information from web sources
- AI-generated summaries would be provided here

**To get real responses:**
1. Configure your Google API key in the .env file
2. Restart the backend service

*Content length: {len(content)} characters from scraped sources*"""
    
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
@app.get("/health")
async def health_check():
    """Health check endpoint to verify backend status and configuration."""
    status = {
        "status": "healthy",
        "services": {
            "firebase": db is not None,
            "google_ai": google_api_key is not None,
            "serpapi": serpapi_api_key is not None,
        },
        "fully_configured": services_initialized,
        "message": "Backend is running"
    }
    
    if not services_initialized:
        status["message"] = "Backend is running but not fully configured. Check logs for missing services."
        
    return status

@app.get("/conversations", response_model=List[ConversationMeta])
async def get_all_conversations():
    """Retrieves metadata for all conversations."""
    if not db:
        raise HTTPException(status_code=503, detail="Database service is not available. Please configure Firebase credentials.")
    
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
    if not db:
        raise HTTPException(status_code=503, detail="Database service is not available. Please configure Firebase credentials.")
    
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

    # Save to Firestore if available
    if db:
        try:
            db.collection('conversations').document(convo_id).set(new_convo.dict())
            print(f"Conversation {convo_id} saved to Firestore")
        except Exception as e:
            print(f"Warning: Could not save conversation to Firestore: {e}")
    else:
        print("Warning: Database not available - conversation not persisted")
    
    return new_convo

