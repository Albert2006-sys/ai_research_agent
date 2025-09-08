import React from 'react';
import ReactMarkdown from 'react-markdown';

const ChatWindow = ({ conversation }) => {
  if (!conversation) return null;

  return (
    <div className="chat-window">
      {conversation.messages.map((message) => (
        <div key={message.id} className={`message-container ${message.role}`}>
          <div className="message-content">
            {message.role === 'model' ? (
              <ReactMarkdown>{message.content}</ReactMarkdown>
            ) : (
              <p>{message.content}</p>
            )}
          </div>
          {message.role === 'model' && message.sources && (
            <div className="sources-section">
              <h4>Sources</h4>
              <div className="sources-list-chat">
                {message.sources.map((source, index) => (
                  <a href={source.url} key={index} target="_blank" rel="noopener noreferrer" className="source-chip">
                    {new URL(source.url).hostname}
                  </a>
                ))}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default ChatWindow;
