// eslint-disable-next-line react/prop-types
function Sidebar({ conversations, onNewChat, onSelectConversation, activeConversationId }) {
  // Add a "guard clause" to handle the initial render when conversations might be undefined.
  if (!conversations) {
    return (
      <aside className="sidebar">
        <button onClick={onNewChat} className="new-chat-btn">+ New Chat</button>
        <div className="history-list">
          <p>Loading...</p>
        </div>
      </aside>
    );
  }
  
  return (
    <aside className="sidebar">
      <button onClick={onNewChat} className="new-chat-btn">+ New Chat</button>
      <div className="history-list">
        {conversations.map((convo) => (
          <div
            key={convo.id}
            className={`history-item ${convo.id === activeConversationId ? 'active' : ''}`}
            onClick={() => onSelectConversation(convo.id)}
          >
            {convo.title}
          </div>
        ))}
      </div>
    </aside>
  );
}

export default Sidebar;

