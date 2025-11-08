# Requirements Document

## Introduction

ClipBrain is a personal PWA that enables a single user to share video URLs from supported platforms (YouTube, Instagram Reels, TikTok, Facebook Reels), automatically download and process the content, transcribe audio, generate structured notes with AI, create semantic embeddings, and provide powerful hybrid search capabilities. The system operates without authentication (security by obscurity), stores videos permanently, prioritizes smallest downloads (audio-first), and uses free-tier services throughout the stack.

## Requirements

### Requirement 1: Platform Support and Content Ingestion

**User Story:** As a user, I want to share public video URLs from supported platforms so that ClipBrain can automatically download and process them for later recall.

#### Acceptance Criteria

1. WHEN a user shares a URL from YouTube (public or unlisted), Instagram Reels (public), TikTok (public), or Facebook Reels (public) THEN the system SHALL accept and queue the URL for processing
2. WHEN a URL points to private, members-only, age-restricted, cookie-gated, or DRM-protected content THEN the system SHALL reject the URL with a clear failure reason code (RESTRICTED_CONTENT_UNSUPPORTED)
3. WHEN downloading media THEN the system SHALL use yt-dlp to download the smallest viable stream that preserves speech content, preferring audio-only formats
4. WHEN a download fails due to platform restrictions THEN the system SHALL terminate processing and display one of the following error codes: RESTRICTED_CONTENT_UNSUPPORTED, NOT_FOUND_OR_REMOVED, or PLATFORM_BLOCKED_TEMPORARILY
5. IF a URL is from an unsupported platform THEN the system SHALL reject it before attempting download
6. WHEN a canonical URL has already been ingested THEN the system SHALL detect the duplicate via URL hash and prevent re-ingestion

### Requirement 2: Media Storage and Persistence

**User Story:** As a user, I want all ingested videos stored permanently so that I can access them indefinitely even if the original source is removed.

#### Acceptance Criteria

1. WHEN media is successfully downloaded THEN the system SHALL upload it to Supabase Storage at path `videos/{video_id}/original.{ext}`
2. WHEN storing media THEN the system SHALL record the storage path in the database `videos.storage_path` column
3. WHEN a user requests media playback THEN the system SHALL generate a signed URL with short TTL from Supabase Storage
4. WHEN generating preview clips THEN the system SHALL store them at `videos/{video_id}/previews/{start_ms}_{end_ms}.mp4`
5. IF storage upload fails THEN the system SHALL retry once and mark the job as failed if retry unsuccessful

### Requirement 3: Transcription Processing

**User Story:** As a user, I want automatic transcription of video audio so that I can search and reference spoken content.

#### Acceptance Criteria

1. WHEN media is successfully stored THEN the system SHALL send it to Deepgram Enhanced Batch API for transcription
2. WHEN requesting transcription THEN the system SHALL request word-level and phrase-level timestamps
3. WHEN transcription completes THEN the system SHALL store the full transcript text in the `transcripts.full_text` column
4. WHEN transcription fails THEN the system SHALL retry once and mark the job as TRANSCRIPTION_FAILED if retry unsuccessful
5. WHEN chunking transcripts THEN the system SHALL create 10-15 second windows with 1-2 second overlap using word timestamps
6. WHEN creating chunks THEN the system SHALL store each chunk with `video_id`, `start_ms`, `end_ms`, and `text` in the `transcript_chunks` table

### Requirement 4: AI-Generated Structured Notes

**User Story:** As a user, I want AI-generated structured notes extracted from video content so that I can quickly understand key information without watching the entire video.

#### Acceptance Criteria

1. WHEN transcription completes THEN the system SHALL send the transcript to Gemini API with a strict JSON schema prompt
2. WHEN generating notes THEN the system SHALL extract: summary (≤8-10 lines), keywords (≤12 terms), insights (bullets), steps (ordered), quotes (with timestamps), and entities (people, tools, URLs)
3. IF video duration is ≥300 seconds (5 minutes) THEN the system SHALL include chapters with titles and start timestamps in the notes
4. IF video duration is <300 seconds THEN the system SHALL omit chapters from the notes
5. WHEN Gemini returns invalid JSON THEN the system SHALL retry once with a clarifier prompt requesting only valid JSON
6. IF JSON validation fails after retry THEN the system SHALL store raw text as `notes_raw_text` and mark status as NOTES_PARTIAL
7. WHEN notes are successfully generated THEN the system SHALL store them in the `notes` table with all structured fields

### Requirement 5: Semantic Search with Embeddings

**User Story:** As a user, I want to search my video library using natural language, concepts, and questions so that I can find relevant content based on meaning, not just keywords.

#### Acceptance Criteria

1. WHEN transcript chunks are created THEN the system SHALL generate embeddings for each chunk using Gemini Embeddings API
2. WHEN generating embeddings THEN the system SHALL batch requests to respect rate limits
3. WHEN embeddings are generated THEN the system SHALL store them in the `transcript_chunks.embedding` vector column
4. WHEN a user submits a search query THEN the system SHALL compute an embedding for the query using Gemini Embeddings
5. WHEN performing vector search THEN the system SHALL use cosine similarity via pgvector IVFFLAT index on `transcript_chunks.embedding`
6. IF embedding generation fails THEN the system SHALL retry once and mark as EMBEDDING_PARTIAL if unsuccessful (keyword search still functional)

### Requirement 6: Hybrid Search and Ranking

**User Story:** As a user, I want to search using tags, keywords, exact phrases, and semantic meaning so that I can find videos through multiple search strategies.

#### Acceptance Criteria

1. WHEN a user submits a search query THEN the system SHALL perform both vector KNN search and full-text search
2. IF the query contains quoted text THEN the system SHALL treat it as an exact phrase filter against transcript and title
3. IF the query appears to be a tag THEN the system SHALL boost tag matches in ranking
4. WHEN merging search results THEN the system SHALL normalize both semantic and keyword scores to [0,1] and compute final_score = 0.6 * semantic + 0.4 * keyword
5. WHEN grouping results THEN the system SHALL group by video_id and keep the top 2-3 spans per video
6. WHEN returning results THEN the system SHALL include: video_id, title, platform, start_ms, end_ms, snippet, score, tags, chapter_title (if applicable), source_url, and deep_link (if supported)
7. WHEN search completes THEN the system SHALL return results within ≤1.5 seconds for typical queries

### Requirement 7: Deep Linking and Preview Playback

**User Story:** As a user, I want to jump directly to relevant timestamps in the original platform or play inline previews so that I can quickly verify search results.

#### Acceptance Criteria

1. WHEN a search result is from YouTube THEN the system SHALL generate a deep_link with `&t={seconds}` parameter pointing to the exact timestamp
2. WHEN a search result is from Instagram, TikTok, or Facebook THEN the system SHALL omit the timestamp parameter from deep_link (not supported by platforms)
3. WHEN displaying any search result THEN the system SHALL provide a signed_play_url for inline preview playback from stored media
4. WHEN generating preview clips THEN the system SHALL use ffmpeg to create 10-12 second MP4 clips with `-c:v libx264 -c:a aac -movflags +faststart`
5. WHEN a user requests to jump to a timestamp THEN the system SHALL return both the deep_link to the original platform and the signed_play_url for inline playback

### Requirement 8: PWA with Share Target Integration

**User Story:** As a user, I want to share videos directly from platform apps to ClipBrain so that ingestion is seamless and native-feeling.

#### Acceptance Criteria

1. WHEN the PWA is installed THEN the system SHALL register as a share target accepting URL and optional text/title
2. WHEN a URL is shared to ClipBrain THEN the system SHALL route to `/share` page and forward to `POST /ingest`
3. WHEN ingestion is queued THEN the system SHALL redirect to `/item/{video_id}` showing live processing status
4. WHEN displaying processing status THEN the system SHALL show which stage is currently running (download, transcribe, notes, embeddings)
5. WHEN a job fails THEN the system SHALL display the exact failure reason code with user-friendly micro-copy
6. WHEN the PWA is accessed offline THEN the system SHALL display an offline shell for the UI (optional enhancement)

### Requirement 9: Job Status and Polling

**User Story:** As a user, I want to see real-time progress of video processing so that I know when content is ready to search.

#### Acceptance Criteria

1. WHEN a video is submitted THEN the system SHALL create a database row with status 'queued'
2. WHEN processing begins THEN the system SHALL update status to 'processing'
3. WHEN processing completes successfully THEN the system SHALL update status to 'done'
4. WHEN processing fails THEN the system SHALL update status to 'failed' and record fail_reason
5. WHEN the frontend polls `GET /job/{job_id}` THEN the system SHALL return current status, video_id, and fail_reason (if applicable)
6. WHEN status changes to 'done' or 'failed' THEN the system SHALL emit an event/log for frontend polling detection

### Requirement 10: Collections and Organization

**User Story:** As a user, I want to organize videos into manual collections and use auto-generated tags so that I can categorize and filter my library.

#### Acceptance Criteria

1. WHEN notes are generated THEN the system SHALL extract keywords as auto-tags and store them in `notes.keywords` array
2. WHEN displaying tags THEN the system SHALL allow the user to edit and add custom tags
3. WHEN a user creates a collection THEN the system SHALL store it in the `collections` table with a unique name
4. WHEN a user adds a video to a collection THEN the system SHALL create a mapping in `collection_items` table
5. WHEN browsing the home screen THEN the system SHALL display tag chips and collection filters for quick navigation

### Requirement 11: Data Export and Backup

**User Story:** As a user, I want to export all my data including videos, transcripts, notes, and embeddings so that I have a complete backup.

#### Acceptance Criteria

1. WHEN a user requests export via `GET /export` THEN the system SHALL generate a ZIP file containing JSON data and media files
2. WHEN exporting JSON THEN the system SHALL include complete data from videos, transcripts, transcript_chunks, notes, and collections tables
3. WHEN exporting media THEN the system SHALL include all original media files and preview clips from Supabase Storage
4. WHEN export completes THEN the system SHALL stream the ZIP file to the user for download

### Requirement 12: No Authentication and Security Model

**User Story:** As the system owner, I want a simple no-auth deployment with security by obscurity so that I can avoid authentication complexity while maintaining reasonable access control.

#### Acceptance Criteria

1. WHEN deploying the system THEN the system SHALL NOT implement any user authentication or session management
2. WHEN configuring the reverse proxy THEN the system SHOULD support optional IP allow-list for `/ingest` and `/export` endpoints
3. WHEN the backend accesses Supabase THEN the system SHALL use service role key held server-side only
4. WHEN the frontend needs media access THEN the system SHALL request signed URLs from the backend with short TTL
5. WHEN storing API keys THEN the system SHALL keep all secrets in server environment variables only, never exposed to frontend

### Requirement 13: Free-Tier Cost Controls

**User Story:** As the system owner, I want the entire system to run on free tiers of services so that I minimize operational costs.

#### Acceptance Criteria

1. WHEN downloading media THEN the system SHALL prefer audio-only formats to minimize storage usage
2. WHEN a canonical URL is already ingested THEN the system SHALL prevent re-ingestion via dedup hash
3. WHEN requesting transcription THEN the system SHALL use Deepgram batch API and cap maximum duration per job at 2 hours
4. WHEN generating embeddings THEN the system SHALL batch requests and cache embeddings per chunk text hash
5. WHEN re-processing content THEN the system SHALL only re-embed chunks if the text has changed
6. WHEN the system is deployed THEN it SHALL run on: Vercel Free (frontend), Fly.io/Railway Free (backend), Upstash Redis Free (queue), Supabase Free (database + storage), Deepgram Free (transcription), and Gemini Free (notes + embeddings)
