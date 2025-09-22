# AI Research Agent Backend

A FastAPI-based backend for an AI research agent that searches the web, scrapes content, and provides AI-generated summaries.

## Features

- **Web Search**: Uses SerpAPI to search Google for relevant sources
- **Content Scraping**: Extracts content from web pages using newspaper3k
- **AI Summarization**: Uses Google Gemini to generate comprehensive summaries
- **Conversation Storage**: Stores research conversations in Firebase Firestore
- **CORS Support**: Configured for frontend integration

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Services (Optional)

The backend will start without configuration but with limited functionality. For full features:

#### Set up Environment Variables
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
GOOGLE_API_KEY=your_google_api_key_here
SERPAPI_API_KEY=your_serpapi_key_here
```

#### Set up Firebase (Optional)
```bash
cp firebase-credentials.json.example firebase-credentials.json
```

Edit `firebase-credentials.json` with your Firebase service account credentials.

### 3. Start the Backend

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

The backend will start on `http://localhost:8000`

## API Endpoints

### Health Check
- **GET** `/health` - Check backend status and service availability

### Conversations
- **GET** `/conversations` - List all conversations (requires Firebase)
- **GET** `/conversations/{id}` - Get specific conversation (requires Firebase)
- **POST** `/conversations` - Create new research conversation
  ```json
  {
    "query": "Your research question here"
  }
  ```

## Service Requirements

| Service | Required For | Configuration |
|---------|--------------|---------------|
| SerpAPI | Web search | `SERPAPI_API_KEY` in .env |
| Google Gemini | AI summaries | `GOOGLE_API_KEY` in .env |
| Firebase Firestore | Conversation storage | `firebase-credentials.json` |

## Running Without Full Configuration

The backend is designed to work even without all services configured:

- **Without SerpAPI**: Will use demo URLs for testing
- **Without Google Gemini**: Will provide formatted demo responses
- **Without Firebase**: Conversations work but are not persisted

This allows for easy development and testing without requiring all external services.

## Getting API Keys

### Google API Key (for Gemini AI)
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file

### SerpAPI Key
1. Sign up at [SerpAPI](https://serpapi.com/)
2. Get your API key from the dashboard
3. Add it to your `.env` file

### Firebase Setup
1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable Firestore Database
3. Create a service account and download the JSON credentials
4. Save as `firebase-credentials.json`

## Development

To see detailed logs and service status, check the console output when starting the backend. The health endpoint also provides service status information.

## Frontend Integration

The backend is configured with CORS to allow frontend connections. The default frontend expects the backend on `http://127.0.0.1:8000`.