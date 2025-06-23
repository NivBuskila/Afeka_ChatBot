// Define common types used across chat components
export interface Message {
  id: number;
  type: 'user' | 'bot';
  content: string;
  timestamp: string;
}

export interface Conversation {
  id: string;
  title: string;
  date: string;
  preview: string;
} 