import { MessageProps } from '../../types/chat';
import { formatTime } from '../../utils';

export const ChatMessage: React.FC<MessageProps> = ({ message, onCopy }) => {
  const isBot = message.type === 'bot';
  
  const handleCopy = () => {
    if (onCopy) {
      onCopy(message.content);
    }
  };

  return (
    <div className={`flex ${isBot ? 'justify-start' : 'justify-end'} mb-4`}>
      <div className={`max-w-[70%] rounded-lg p-3 ${
        isBot ? 'bg-black bg-opacity-20' : 'bg-green-500 bg-opacity-10'
      }`}>
        <div className="text-sm text-green-400 mb-1">
          {formatTime(message.timestamp)}
        </div>
        <p className="text-white">{message.content}</p>
        {isBot && (
          <button 
            onClick={handleCopy}
            className="text-green-400 text-sm mt-2 opacity-50 hover:opacity-100"
          >
            Copy
          </button>
        )}
      </div>
    </div>
  );
};