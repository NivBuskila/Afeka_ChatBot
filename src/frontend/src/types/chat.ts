export interface Message {
    id: string;
    content: string;
    type: 'user' | 'bot';
    timestamp: Date;
  }
  
  export interface ChatProps {
    messages: Message[];
    onSendMessage: (message: string) => void;
    isLoading?: boolean;
  }
  
  export interface MessageProps {
    message: Message;
    onCopy?: (content: string) => void;
  }