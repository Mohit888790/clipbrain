# Implementation Plan

- [x] 1. Set up database schema and infrastructure
  - Create Supabase project and enable pgvector extension
  - Create all tables (videos, transcripts, transcript_chunks, notes, collections, collection_items) with proper constraints and foreign keys
  - Create indexes: IVFFLAT for embeddings, GIN for full-text search, trigram for title search, and standard indexes for foreign keys
  - Set up Supabase Storage bucket named "videos" with appropriate policies
  - Configure Upstash Redis instance and obtain connection URL
  - _Requirements: 2.1, 2.2, 3.4, 5.3, 6.5, 10.3_

- [x] 2. Initialize backend FastAPI project structure
  - Create FastAPI project with async support and proper directory structure (services/, models/, routes/, workers/)
  - Set up Docker container with Python 3.11, ffmpeg, and yt-dlp installed
  - Configure environment variable loading for API keys and service URLs
  - Create database connection module using asyncpg with connection pooling
  - Create Supabase Storage client wrapper for uploads and signed URL generation
  - _Requirements: 1.3, 2.1, 2.3, 12.3, 12.5_

- [x] 3. Implement media downloader service
  - [x] 3.1 Create URL canonicalization and platform detection logic
    - Write function to normalize URLs to canonical format (e.g., YouTube shorts → watch?v=)
    - Implement platform detection from URL domain (youtube.com, instagram.com, tiktok.com, facebook.com)
    - Create allowlist validation to reject unsupported platforms
    - _Requirements: 1.1, 1.5_
  
  - [x] 3.2 Implement yt-dlp wrapper with error classification
    - Create async wrapper around yt-dlp subprocess with format string "bestaudio[ext=m4a]/bestaudio/best"
    - Add flags: --no-playlist --no-warnings --retries 2 --socket-timeout 30
    - Parse yt-dlp errors and classify into error codes (RESTRICTED_CONTENT_UNSUPPORTED, NOT_FOUND_OR_REMOVED, PLATFORM_BLOCKED_TEMPORARILY)
    - Extract metadata (title, duration, language) from yt-dlp JSON output
    - _Requirements: 1.3, 1.4, 1.6_
  
  - [x] 3.3 Implement ffprobe integration for media inspection
    - Create async wrapper for ffprobe to extract duration_seconds, audio codec, and container format
    - Add language hint detection from metadata
    - _Requirements: 1.3_

- [x] 4. Implement storage service
  - Create upload_media function to upload files to Supabase Storage at path videos/{video_id}/original.{ext}
  - Implement generate_signed_url function with configurable TTL (default 900 seconds)
  - Create upload_preview function for preview clips at videos/{video_id}/previews/{start_ms}_{end_ms}.mp4
  - Add retry logic (1 retry with 10-second delay) for upload failures
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 7.3_

- [x] 5. Implement transcription service
  - Create Deepgram API client with Enhanced Batch model configuration
  - Implement transcribe function that accepts signed storage URL and requests word/phrase timestamps
  - Parse Deepgram response to extract full_text and word-level timestamps
  - Add retry logic (1 retry with 10-second delay) for transcription failures
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 6. Implement transcript chunking logic
  - Create chunking algorithm that uses word timestamps to create 10-15 second windows with 1-2 second overlap
  - Ensure chunks don't cut mid-sentence by snapping to word boundaries
  - Generate text_hash for each chunk (SHA-256 of normalized text) for caching
  - Store chunks in transcript_chunks table with video_id, start_ms, end_ms, text, and text_hash
  - _Requirements: 3.5, 3.6, 5.3_

- [x] 7. Implement AI service for notes and embeddings
  - [x] 7.1 Create Gemini API client for notes generation
    - Configure Gemini API client with text generation model
    - Create strict JSON schema prompt for notes extraction (summary, keywords, insights, steps, quotes, entities)
    - Add conditional logic: include chapters only if duration_seconds >= 300
    - Implement JSON validation with retry mechanism (1 retry with clarifier prompt)
    - Handle partial failures by storing raw text as notes_raw_text
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_
  
  - [x] 7.2 Create Gemini Embeddings client
    - Configure Gemini Embeddings API client with text-embedding-004 model
    - Implement generate_embedding function for single text
    - Implement batch_embeddings function that respects rate limits (60 req/min, 1500 req/day)
    - Add embedding cache lookup by text_hash before generating new embeddings
    - _Requirements: 5.1, 5.2, 5.3, 5.6_

- [x] 8. Implement worker pipeline with RQ
  - [x] 8.1 Set up RQ worker infrastructure
    - Configure RQ connection to Upstash Redis
    - Create worker process that listens to 'default' queue with 30-minute timeout
    - Implement job status tracking in database (queued → processing → done/failed)
    - _Requirements: 9.1, 9.2, 9.3, 9.4_
  
  - [x] 8.2 Implement main pipeline orchestration
    - Create process_video job function that executes all pipeline stages sequentially
    - Add idempotency check using canonical_url_hash before starting pipeline
    - Update video status and current_stage at each step
    - Implement comprehensive error handling with fail_reason recording
    - _Requirements: 1.6, 9.5, 9.6_
  
  - [x] 8.3 Wire pipeline stages together
    - Stage 1: Download media using MediaDownloader service
    - Stage 2: Upload to storage using StorageService
    - Stage 3: Transcribe using TranscriptionService
    - Stage 4: Generate notes using AIService
    - Stage 5: Chunk transcript and generate embeddings
    - Stage 6: Generate preview clips using ffmpeg (optional)
    - Update status to 'done' on success or 'failed' with reason on error
    - _Requirements: 1.3, 2.1, 3.1, 4.1, 5.1, 7.4_

- [x] 9. Implement preview clip generation
  - Create generate_preview function using ffmpeg with command: -ss {start} -t {duration} -i {input} -c:v libx264 -c:a aac -movflags +faststart {output}
  - Generate 10-12 second clips for each chunk (or top chunks only)
  - Upload preview clips to storage using upload_preview function
  - Make preview generation optional/async to not block main pipeline
  - _Requirements: 2.4, 7.4, 7.5_

- [x] 10. Implement search service with hybrid ranking
  - [x] 10.1 Create vector search function
    - Implement KNN search on transcript_chunks.embedding using pgvector cosine similarity
    - Limit to top 50 candidates for efficiency
    - Return results with video_id, start_ms, end_ms, text, and similarity score
    - _Requirements: 5.4, 5.5, 6.1_
  
  - [x] 10.2 Create full-text search function
    - Implement PostgreSQL full-text search using to_tsvector on transcripts.full_text
    - Add trigram search on videos.title for fuzzy matching
    - Handle exact phrase queries (quoted text) with phrase matching
    - Return results with video_id, snippet, and relevance score
    - _Requirements: 6.1, 6.2_
  
  - [x] 10.3 Implement hybrid ranking and result merging
    - Normalize vector scores and text scores to [0,1] range
    - Calculate final_score = 0.6 * semantic_score + 0.4 * keyword_score
    - Merge and deduplicate results from both search methods
    - Group results by video_id and keep top 2-3 spans per video
    - Sort by final_score descending
    - _Requirements: 6.4, 6.5_
  
  - [x] 10.4 Add result decoration with metadata
    - Attach chapter_title if span falls within a chapter time range
    - Generate deep_link for YouTube with &t={seconds} parameter
    - Omit timestamp parameter for Instagram, TikTok, Facebook (not supported)
    - Generate signed_play_url for inline preview playback
    - Include tags from notes.keywords
    - _Requirements: 6.6, 7.1, 7.2, 7.3_

- [x] 11. Implement FastAPI routes
  - [x] 11.1 Create POST /ingest endpoint
    - Validate URL format and platform
    - Generate canonical_url_hash and check for duplicates
    - Create video record with status 'queued'
    - Enqueue job to RQ with video_id and source_url
    - Return job_id and video_id
    - _Requirements: 1.1, 1.5, 1.6, 9.1_
  
  - [x] 11.2 Create GET /job/{job_id} endpoint
    - Query video status from database
    - Return status, video_id, fail_reason, and current_stage
    - _Requirements: 9.5_
  
  - [x] 11.3 Create GET /item/{video_id} endpoint
    - Fetch video details, notes, and transcript preview (first N chunks)
    - Generate signed URL for storage_path
    - Return complete video object with all metadata
    - _Requirements: 2.3, 10.1_
  
  - [x] 11.4 Create POST /search endpoint
    - Accept query string, optional top_k, tags filter, and platform filter
    - Generate query embedding using AIService
    - Execute hybrid search using SearchService
    - Return results within 1.5 second target
    - _Requirements: 5.4, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_
  
  - [x] 11.5 Create GET /jump endpoint
    - Accept video_id and start_ms query parameters
    - Generate deep_link with timestamp for YouTube, without for others
    - Generate signed_play_url for inline playback
    - Return both URLs and start_seconds
    - _Requirements: 7.1, 7.2, 7.5_
  
  - [x] 11.6 Create GET /export endpoint
    - Query all videos, transcripts, chunks, notes, and collections
    - Generate JSON files for each table
    - Download media files from Supabase Storage
    - Create ZIP archive with JSON + media files
    - Stream ZIP to client
    - _Requirements: 11.1, 11.2, 11.3_
  
  - [x] 11.7 Create GET /healthz endpoint
    - Check Redis connection
    - Check Supabase connection
    - Return health status and timestamp
    - _Requirements: 12.1_

- [x] 12. Implement collections management
  - Create POST /collections endpoint to create new collection with unique name
  - Create POST /collections/{id}/items endpoint to add video to collection
  - Create DELETE /collections/{id}/items/{video_id} endpoint to remove video from collection
  - Create GET /collections endpoint to list all collections with video counts
  - Create GET /collections/{id} endpoint to get collection details with videos
  - _Requirements: 10.1, 10.2, 10.3, 10.4_

- [x] 13. Implement tag management
  - Create PATCH /item/{video_id}/tags endpoint to update notes.keywords array
  - Add tag filtering to search endpoint using array overlap query
  - _Requirements: 10.2, 10.5_

- [x] 14. Add rate limiting and security
  - Implement rate limiting middleware using Redis: 10 requests/hour per IP for /ingest, 100 requests/hour for /search
  - Add input validation for all endpoints (URL format, query length, collection names)
  - Add URL sanitization to reject localhost, internal IPs, and suspicious patterns
  - Configure CORS to allow frontend domain only
  - _Requirements: 12.1, 12.2_

- [x] 15. Initialize Next.js PWA frontend project
  - Create Next.js 14+ project with App Router and TypeScript
  - Install and configure Tailwind CSS
  - Set up PWA manifest with name "ClipBrain", icons, and Share Target API configuration
  - Configure service worker for offline UI shell (optional)
  - Set up API client with base URL from environment variable
  - _Requirements: 8.1, 8.2, 8.3_

- [ ] 16. Implement frontend API client
  - Create typed API client functions for all backend endpoints (ingest, job status, item, search, jump, export)
  - Add error handling and retry logic for network failures
  - Implement polling utility for job status with exponential backoff
  - _Requirements: 8.2, 9.5_

- [ ] 17. Build core UI components
  - [ ] 17.1 Create SearchBar component
    - Input field with support for tags (prefix with #), exact phrases (quoted), and natural language
    - Display search suggestions and recent searches
    - Handle Enter key and search button click
    - _Requirements: 6.1, 6.2, 6.3, 8.3_
  
  - [ ] 17.2 Create ResultCard component
    - Display title, platform chip, snippet with highlighted matches, timestamp, and score
    - Add "Open in app" button that uses deep_link
    - Add "Preview" button that opens inline player with signed_play_url
    - Show tags as chips
    - Display chapter_title if available
    - _Requirements: 6.6, 7.1, 7.2, 7.3, 8.3_
  
  - [ ] 17.3 Create VideoPlayer component
    - HTML5 video player for inline preview playback
    - Accept signed URL and start position
    - Show loading state and error handling
    - _Requirements: 7.3, 7.5_
  
  - [ ] 17.4 Create StatusIndicator component
    - Visual progress bar showing pipeline stages (download → transcribe → notes → embeddings)
    - Display current stage with icon and label
    - Show error messages with user-friendly micro-copy for failure codes
    - _Requirements: 8.3, 8.4, 9.5_
  
  - [ ] 17.5 Create ChapterTOC component
    - List of chapters with titles and timestamps (only for videos >= 5 minutes)
    - Clickable chapters that jump to timestamp
    - _Requirements: 4.3, 8.3_
  
  - [ ] 17.6 Create TagChips component
    - Display tags as colored chips
    - Support editing mode to add/remove tags
    - Click to filter search by tag
    - _Requirements: 10.2, 10.5, 8.3_

- [ ] 18. Build frontend pages
  - [ ] 18.1 Create HomePage (/)
    - Large search bar at top
    - "Recent" videos list showing last 20 ingested videos
    - Tag cloud with popular tags
    - Collection filter dropdown
    - _Requirements: 8.3, 10.5_
  
  - [ ] 18.2 Create SearchResultsPage (/search)
    - Display search query and result count
    - List of ResultCard components grouped by video
    - Show query time in milliseconds
    - Empty state when no results found
    - _Requirements: 6.6, 6.7, 8.3_
  
  - [ ] 18.3 Create ItemPage (/item/[id])
    - Video title, platform chip, duration, and creation date
    - Summary section with AI-generated summary
    - Tags section with editable TagChips
    - Chapters table (if available) with ChapterTOC
    - Insights and steps sections
    - Quotes section with timestamps
    - Entities section (people, tools, URLs)
    - Transcript viewer with lazy loading
    - "Open in original" button and preview player
    - _Requirements: 4.2, 4.3, 7.1, 8.3, 10.2_
  
  - [ ] 18.4 Create SharePage (/share)
    - Receive shared URL from Share Target API
    - Display URL being processed
    - Call POST /ingest endpoint
    - Redirect to /item/{video_id} with processing view
    - _Requirements: 8.2, 8.3_
  
  - [ ] 18.5 Create ProcessingView (embedded in ItemPage)
    - Poll GET /job/{job_id} every 2 seconds
    - Display StatusIndicator with current stage
    - Show estimated time remaining (optional)
    - Display failure message with error code if failed
    - Auto-refresh page when status becomes 'done'
    - _Requirements: 8.3, 8.4, 9.5_
  
  - [ ] 18.6 Create CollectionsPage (/collections)
    - List all collections with video counts
    - Create new collection form
    - Click collection to view videos in that collection
    - _Requirements: 10.1, 10.3, 10.4_
  
  - [ ] 18.7 Create ExportPage (/export)
    - Button to trigger GET /export
    - Progress indicator during ZIP generation
    - Auto-download ZIP when ready
    - _Requirements: 11.1, 11.2, 11.3_

- [ ] 19. Implement PWA Share Target integration
  - Configure manifest.json with share_target accepting url and text
  - Create API route /api/share that receives POST from Share Target
  - Forward shared URL to backend /ingest endpoint
  - Redirect to /item/{video_id} page
  - _Requirements: 8.1, 8.2_

- [ ] 20. Add error handling micro-copy
  - Create error message mapping for all failure codes (RESTRICTED_CONTENT_UNSUPPORTED, NOT_FOUND_OR_REMOVED, etc.)
  - Display user-friendly messages in StatusIndicator and error toasts
  - Add retry button for transient failures
  - _Requirements: 8.4_

- [x] 21. Deploy backend to Fly.io
  - Create Dockerfile with Python 3.11, ffmpeg, and yt-dlp
  - Create fly.toml configuration with service ports and environment variables
  - Set up environment variables for all API keys and service URLs
  - Deploy FastAPI app and RQ worker to Fly.io
  - Configure health check endpoint
  - _Requirements: 12.1, 12.4, 12.5, 13.1_

- [ ] 22. Deploy frontend to Vercel
  - Create vercel.json with build configuration
  - Set NEXT_PUBLIC_API_URL environment variable to Fly.io backend URL
  - Deploy Next.js app to Vercel
  - Verify PWA manifest and service worker are served correctly
  - Test Share Target API from mobile device
  - _Requirements: 12.1, 12.4, 13.1_

- [ ] 23. Configure monitoring and logging
  - Add structured logging with structlog to all backend services
  - Log job_id, video_id, stage, duration_ms, and status for all pipeline events
  - Set up basic metrics tracking: jobs processed, average latency, failure rate by error code
  - Configure log aggregation (optional: use Fly.io logs or external service)
  - _Requirements: 12.1_

- [ ]* 24. End-to-end testing
  - [ ]* 24.1 Test YouTube ingestion
    - Share public YouTube video URL
    - Verify status progresses through all stages
    - Verify transcript, notes, chunks, and embeddings are created
    - Search for content from video and verify results
    - Click deep link and verify YouTube URL includes timestamp parameter
    - _Requirements: 1.1, 1.3, 3.1, 4.1, 5.1, 6.1, 7.1_
  
  - [ ]* 24.2 Test Instagram Reels ingestion
    - Share public Instagram Reel URL
    - Verify successful processing
    - Search for content and verify inline preview works
    - Verify deep link does not include timestamp parameter
    - _Requirements: 1.1, 7.2, 7.3_
  
  - [ ]* 24.3 Test TikTok ingestion
    - Share public TikTok URL
    - Verify successful processing
    - Test search and preview functionality
    - _Requirements: 1.1_
  
  - [ ]* 24.4 Test error scenarios
    - Share private video URL and verify RESTRICTED_CONTENT_UNSUPPORTED error
    - Share invalid URL and verify rejection
    - Test with removed video and verify NOT_FOUND_OR_REMOVED error
    - _Requirements: 1.2, 1.4_
  
  - [ ]* 24.5 Test search functionality
    - Test natural language question search
    - Test exact phrase search with quotes
    - Test tag filtering
    - Verify results return within 1.5 seconds
    - _Requirements: 6.1, 6.2, 6.3, 6.7_
  
  - [ ]* 24.6 Test collections and tags
    - Create collection and add videos
    - Edit tags on a video
    - Filter by collection and tags
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [ ]* 24.7 Test export functionality
    - Trigger export and download ZIP
    - Verify ZIP contains JSON files and media files
    - Verify JSON data completeness
    - _Requirements: 11.1, 11.2, 11.3_

- [ ]* 25. Performance optimization
  - [ ]* 25.1 Optimize search latency
    - Profile vector search query time
    - Tune IVFFLAT index parameters (lists count)
    - Add query result caching for popular searches (optional)
    - _Requirements: 6.7, 13.5_
  
  - [ ]* 25.2 Optimize storage usage
    - Verify audio-only downloads are significantly smaller than video
    - Implement embedding cache by text_hash to avoid re-generation
    - Monitor Supabase storage usage and set up alerts
    - _Requirements: 1.3, 13.1, 13.2, 13.4, 13.5_
  
  - [ ]* 25.3 Optimize API quota usage
    - Implement request batching for Gemini Embeddings (up to 100 texts per request)
    - Add rate limit tracking for Deepgram and Gemini
    - Set up alerts when approaching quota limits
    - _Requirements: 5.2, 13.3, 13.4, 13.6_
