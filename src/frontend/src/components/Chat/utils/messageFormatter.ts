export interface Message {
  id: string;
  type: "user" | "bot";
  content: string;
  timestamp: string;
  sessionId?: string;
  chunkText?: string;
}

export function detectMessageType(msg: any, index: number): 'bot' | 'user' {
  // Bot detection logic with fallback for old conversations
  if (msg.role === "bot" || msg.role === "assistant") {
    return 'bot';
  } else if (msg.is_bot === true || msg.is_bot === 1) {
    return 'bot';
  } else if (msg.role === "user" && index % 2 === 1) {
    return 'bot';
  } else if (msg.content && msg.content.length > 100 && msg.role === "user") {
    return 'bot';
  }
  
  return 'user';
}

export function formatMessage(msg: any, index: number, sessionId: string): Message {
  const isBot = detectMessageType(msg, index) === 'bot';
  
  const messageContent = msg.content || msg.message_text || msg.text || "";
  const messageId = msg.id || msg.message_id || `msg-${Date.now()}-${index}`;
  
  return {
    id: messageId,
    type: isBot ? "bot" : "user",
    content: messageContent,
    timestamp: new Date(msg.created_at).toLocaleTimeString(),
    sessionId: msg.chat_session_id || msg.conversation_id || sessionId,
  };
}

export function formatMessages(messages: any[], sessionId: string): Message[] {
  return messages.map((msg, index) => formatMessage(msg, index, sessionId));
} 