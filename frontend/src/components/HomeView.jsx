import { useState } from 'react';
import PropTypes from 'prop-types';

// The HomeView should only be responsible for starting a NEW research query.
// It should not render the sidebar.
function HomeView({ onStartResearch }) {
  const [query, setQuery] = useState('');

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && query) {
      onStartResearch(query);
    }
  };

  return (
    <div className="home-view">
      <div className="home-content">
        <h1 className="home-title">AI Research Agent</h1>
        <p className="home-subtitle">Your intelligent assistant for automated web research and analysis.</p>
        <div className="home-input-container">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask anything..."
          />
          <button onClick={() => onStartResearch(query)} disabled={!query}>
            →
          </button>
        </div>
      </div>
    </div>
  );
}

HomeView.propTypes = {
  onStartResearch: PropTypes.func.isRequired,
};

export default HomeView;

