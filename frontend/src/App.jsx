import { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';
import HomeView from './components/HomeView';

const API_URL = 'http://127.0.0.1:8000';

function App() {
  const [conversations, setConversations] = useState([]);
  const [activeConversation, setActiveConversation] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Fetches the list of conversation titles when the app first loads
  const fetchConversations = async () => {
    try {
      setError('');
      const response = await axios.get(`${API_URL}/conversations`);
      setConversations(response.data);
    } catch (err) {
      console.error("Failed to fetch conversations:", err);
      setError("Could not load conversation history. Is the backend running?");
    }
  };

  useEffect(() => {
    fetchConversations();
  }, []);

  // Clears the main window to show the home screen
  const handleNewChat = () => {
    setActiveConversation(null);
  };

  // Fetches the full content of a selected conversation from the sidebar
  const handleSelectConversation = async (convoId) => {
    try {
      setError('');
      setIsLoading(true);
      const response = await axios.get(`${API_URL}/conversations/${convoId}`);
      setActiveConversation(response.data);
    } catch (err) {
      console.error(`Failed to fetch conversation ${convoId}:`, err);
      setError("Could not load this conversation.");
    } finally {
      setIsLoading(false);
    }
  };

  // Starts a new research task from the home screen
  const handleStartNewResearch = async (query) => {
    try {
      setError('');
      setIsLoading(true);
      setActiveConversation(null); // Clear any active conversation
      const response = await axios.post(`${API_URL}/conversations`, { query });
      const newConvo = response.data;
      
      // Add the new conversation to the top of the sidebar list and make it active
      setConversations([{ id: newConvo.id, title: newConvo.title }, ...conversations]);
      setActiveConversation(newConvo);
    } catch (err) {
        console.error("Failed to start new research:", err);
        setError(err.response?.data?.detail || "Failed to start new research.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="layout-container">
      <Sidebar 
        conversations={conversations}
        onNewChat={handleNewChat}
        onSelectConversation={handleSelectConversation}
        activeConversationId={activeConversation?.id}
        isMobileOpen={isMobileMenuOpen}
        onMobileClose={() => setIsMobileMenuOpen(false)}
      />
      
      <main className="main-content">
        {/* Mobile Menu Toggle */}
        <button 
          className="mobile-menu-toggle"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          aria-label="Toggle menu"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 12H21M3 6H21M3 18H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>

        {error && <div className="error-banner">{error}</div>}

        {/* Show a loading spinner only when starting a new chat */}
        {isLoading && !activeConversation && (
            <div className="loader-container">
                <div className="loader"></div>
                <p>Starting new research...</p>
            </div>
        )}
        
        {/* Show the Home view if there's no active conversation and it's not loading a new one */}
        {!isLoading && !activeConversation && (
          <HomeView onStartResearch={handleStartNewResearch} />
        )}
        
        {/* Show the Chat window if there is an active conversation */}
        {activeConversation && (
          <ChatWindow conversation={activeConversation} isLoading={isLoading} />
        )}
      </main>
    </div>
  );
}

export default App;

