import { useState, useEffect, useMemo } from 'react';
import PropTypes from 'prop-types';

// The HomeView should only be responsible for starting a NEW research query.
// It should not render the sidebar.
function HomeView({ onStartResearch }) {
  const [query, setQuery] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && query) {
      onStartResearch(query);
    }
  };

  const handleInputChange = (e) => {
    setQuery(e.target.value);
    setIsTyping(true);
    
    // Clear typing indicator after user stops typing
    clearTimeout(window.typingTimeout);
    window.typingTimeout = setTimeout(() => {
      setIsTyping(false);
    }, 1000);
  };

  const exampleQueries = useMemo(() => [
    "How does artificial intelligence work?",
    "What are the latest trends in renewable energy?",
    "Explain quantum computing",
    "Best practices for web development",
    "Climate change impact on agriculture"
  ], []);

  const [displayText, setDisplayText] = useState('');
  const [placeholderIndex, setPlaceholderIndex] = useState(0);
  const [charIndex, setCharIndex] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    if (query) return; // Don't animate if user has typed something

    const currentQuery = exampleQueries[placeholderIndex];
    const typingSpeed = isDeleting ? 50 : 100;
    const pauseTime = isDeleting ? 500 : 2000;

    const timeout = setTimeout(() => {
      if (!isDeleting && charIndex < currentQuery.length) {
        setDisplayText(currentQuery.slice(0, charIndex + 1));
        setCharIndex(charIndex + 1);
      } else if (isDeleting && charIndex > 0) {
        setDisplayText(currentQuery.slice(0, charIndex - 1));
        setCharIndex(charIndex - 1);
      } else if (!isDeleting && charIndex === currentQuery.length) {
        setTimeout(() => setIsDeleting(true), pauseTime);
      } else if (isDeleting && charIndex === 0) {
        setIsDeleting(false);
        setPlaceholderIndex((prev) => (prev + 1) % exampleQueries.length);
      }
    }, typingSpeed);

    return () => clearTimeout(timeout);
  }, [charIndex, isDeleting, placeholderIndex, query, exampleQueries]);

  return (
    <div className="home-view">
      <div className="home-content">
        <h1 className="home-title">AI Research Agent</h1>
        <p className="home-subtitle">Your intelligent assistant for automated web research and analysis.</p>
        
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🔍</div>
            <h3>Smart Search</h3>
            <p>Advanced web scraping and analysis</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🧠</div>
            <h3>AI-Powered</h3>
            <p>Intelligent summarization and insights</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">⚡</div>
            <h3>Real-time</h3>
            <p>Fast and accurate research results</p>
          </div>
        </div>

        <div className="home-input-container">
          <input
            type="text"
            value={query}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            placeholder={query ? "Ask anything..." : displayText || "Ask anything..."}
            className={isTyping ? 'typing' : ''}
          />
          <button 
            onClick={() => onStartResearch(query)} 
            disabled={!query}
            className={query ? 'ready' : ''}
          >
            →
          </button>
        </div>
        
        <div className="example-queries">
          <p>Try asking:</p>
          <div className="query-chips">
            {exampleQueries.slice(0, 3).map((example, index) => (
              <button
                key={index}
                className="query-chip"
                onClick={() => setQuery(example)}
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

HomeView.propTypes = {
  onStartResearch: PropTypes.func.isRequired,
};

export default HomeView;

