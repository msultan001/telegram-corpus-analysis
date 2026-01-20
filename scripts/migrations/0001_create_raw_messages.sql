-- Initial migration: create raw_messages table
CREATE TABLE IF NOT EXISTS raw_messages (
  id SERIAL PRIMARY KEY,
  channel_id BIGINT,
  channel_name TEXT,
  message_id BIGINT,
  date_key DATE,
  text TEXT,
  metadata JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  UNIQUE(channel_name, message_id)
);
