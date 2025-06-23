-- Migration: Create or replace messages table with advanced schema
DROP TABLE IF EXISTS public.messages CASCADE;

CREATE TABLE public.messages (
  message_id bigserial NOT NULL,
  conversation_id uuid NOT NULL,
  user_id uuid NOT NULL,
  request text NULL,
  response text NULL,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  status text NOT NULL DEFAULT 'RECEIVED'::text,
  status_updated_at timestamp with time zone NOT NULL DEFAULT now(),
  error_message text NULL,
  request_type text NULL DEFAULT 'TEXT'::text,
  request_payload jsonb NULL,
  response_payload jsonb NULL,
  status_code integer NULL,
  processing_start_time timestamp with time zone NULL,
  processing_end_time timestamp with time zone NULL,
  processing_time_ms integer NULL,
  is_sensitive boolean NULL DEFAULT false,
  metadata jsonb NULL DEFAULT '{}'::jsonb,
  chat_session_id uuid NULL,
  CONSTRAINT messages_pkey PRIMARY KEY (message_id),
  CONSTRAINT messages_chat_session_id_fkey FOREIGN KEY (chat_session_id) REFERENCES chat_sessions (id),
  CONSTRAINT messages_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES conversations (conversation_id) ON DELETE CASCADE,
  CONSTRAINT messages_user_id_fkey FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
) TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON public.messages USING btree (conversation_id) TABLESPACE pg_default;
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON public.messages USING btree (user_id) TABLESPACE pg_default;
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON public.messages USING btree (created_at) TABLESPACE pg_default;
CREATE INDEX IF NOT EXISTS idx_messages_status ON public.messages USING btree (status) TABLESPACE pg_default;
