// Data types for Supabase
// Auto-generated file to resolve missing import issues

export type UserProfile = {
  id: string;
  email?: string;
  username?: string;
  full_name?: string;
  avatar_url?: string;
  created_at?: string;
  updated_at?: string;
};

export type Message = {
  id: string;
  user_id: string;
  content: string;
  created_at: string;
  is_bot?: boolean;
};

export type ChatSession = {
  id: string;
  user_id: string;
  title?: string;
  created_at: string;
  updated_at?: string;
  messages?: Message[];
};

export type SupabaseError = {
  message: string;
  status?: number;
  code?: string;
};

export enum AuthProviders {
  EMAIL = "email",
  GOOGLE = "google",
  GITHUB = "github",
}

export type AuthSession = {
  user: UserProfile;
  session: {
    access_token: string;
    refresh_token?: string;
    expires_at?: number;
  };
};

export type DatabaseSchema = {
  public: {
    Tables: {
      user_profiles: {
        Row: UserProfile;
        Insert: Omit<UserProfile, "id" | "created_at">;
        Update: Partial<Omit<UserProfile, "id">>;
      };
      messages: {
        Row: Message;
        Insert: Omit<Message, "id" | "created_at">;
        Update: Partial<Omit<Message, "id">>;
      };
      chat_sessions: {
        Row: ChatSession;
        Insert: Omit<ChatSession, "id" | "created_at">;
        Update: Partial<Omit<ChatSession, "id">>;
      };
    };
  };
}; 