import PropTypes from 'prop-types';

function Sidebar({ conversations, onNewChat, onSelectConversation, activeConversationId, isMobileOpen, onMobileClose }) {
  // Add a "guard clause" to handle the initial render when conversations might be undefined.
  if (!conversations) {
    return (
      <aside className={`sidebar ${isMobileOpen ? 'open' : ''}`}>
        <button onClick={onNewChat} className="new-chat-btn">+ New Chat</button>
        <div className="history-list">
          <p>Loading...</p>
        </div>
      </aside>
    );
  }
  
  return (
    <aside className={`sidebar ${isMobileOpen ? 'open' : ''}`}>
      <button onClick={onNewChat} className="new-chat-btn">+ New Chat</button>
      <div className="history-list">
        {conversations.map((convo) => (
          <div
            key={convo.id}
            className={`history-item ${convo.id === activeConversationId ? 'active' : ''}`}
            onClick={() => {
              onSelectConversation(convo.id);
              if (onMobileClose) onMobileClose();
            }}
          >
            {convo.title}
          </div>
        ))}
      </div>
    </aside>
  );
}

Sidebar.propTypes = {
  conversations: PropTypes.array,
  onNewChat: PropTypes.func.isRequired,
  onSelectConversation: PropTypes.func.isRequired,
  activeConversationId: PropTypes.string,
  isMobileOpen: PropTypes.bool,
  onMobileClose: PropTypes.func,
};

export default Sidebar;

