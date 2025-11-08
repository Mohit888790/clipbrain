-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable pg_trgm for trigram search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Videos table
CREATE TABLE videos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_url TEXT NOT NULL,
  canonical_url_hash TEXT UNIQUE NOT NULL,
  storage_path TEXT,
  platform TEXT NOT NULL CHECK (platform IN ('youtube', 'instagram', 'tiktok', 'facebook')),
  title TEXT,
  duration_seconds INTEGER,
  language TEXT,
  status TEXT NOT NULL CHECK (status IN ('queued', 'processing', 'done', 'failed')),
  fail_reason TEXT,
  current_stage TEXT CHECK (current_stage IN ('download', 'upload', 'transcribe', 'notes', 'embeddings', 'previews')),
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes for videos table
CREATE INDEX idx_videos_status ON videos(status);
CREATE INDEX idx_videos_created ON videos(created_at DESC);
CREATE INDEX idx_videos_canonical ON videos(canonical_url_hash);
CREATE INDEX idx_videos_platform ON videos(platform);
CREATE INDEX idx_videos_title_trgm ON videos USING gin(title gin_trgm_ops);

-- Transcripts table
CREATE TABLE transcripts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  full_text TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes for transcripts table
CREATE INDEX idx_transcripts_video ON transcripts(video_id);
CREATE INDEX idx_transcripts_fulltext ON transcripts USING gin(to_tsvector('simple', full_text));

-- Transcript chunks table
CREATE TABLE transcript_chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  start_ms INTEGER NOT NULL,
  end_ms INTEGER NOT NULL,
  text TEXT NOT NULL,
  text_hash TEXT NOT NULL,
  embedding VECTOR(768),
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes for transcript_chunks table
CREATE INDEX idx_chunks_video ON transcript_chunks(video_id, start_ms);
CREATE INDEX idx_chunks_text_hash ON transcript_chunks(text_hash);
CREATE INDEX idx_chunks_embedding ON transcript_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Notes table
CREATE TABLE notes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  summary TEXT,
  keywords TEXT[] DEFAULT '{}',
  chapters JSONB DEFAULT '[]',
  insights JSONB DEFAULT '[]',
  steps JSONB DEFAULT '[]',
  quotes JSONB DEFAULT '[]',
  entities JSONB DEFAULT '{}',
  notes_raw_text TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes for notes table
CREATE INDEX idx_notes_video ON notes(video_id);
CREATE INDEX idx_notes_keywords ON notes USING gin(keywords);

-- Collections table
CREATE TABLE collections (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT UNIQUE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Collection items junction table
CREATE TABLE collection_items (
  collection_id UUID NOT NULL REFERENCES collections(id) ON DELETE CASCADE,
  video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  added_at TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (collection_id, video_id)
);

-- Indexes for collection_items table
CREATE INDEX idx_collection_items_video ON collection_items(video_id);
CREATE INDEX idx_collection_items_collection ON collection_items(collection_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update updated_at on videos table
CREATE TRIGGER update_videos_updated_at
  BEFORE UPDATE ON videos
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();
