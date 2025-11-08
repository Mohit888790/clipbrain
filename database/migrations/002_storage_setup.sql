-- Create storage bucket for videos
INSERT INTO storage.buckets (id, name, public)
VALUES ('videos', 'videos', false)
ON CONFLICT (id) DO NOTHING;

-- Storage policies for videos bucket
-- Policy: Allow service role to upload files
CREATE POLICY "Service role can upload videos"
ON storage.objects FOR INSERT
TO service_role
WITH CHECK (bucket_id = 'videos');

-- Policy: Allow service role to read files
CREATE POLICY "Service role can read videos"
ON storage.objects FOR SELECT
TO service_role
USING (bucket_id = 'videos');

-- Policy: Allow service role to update files
CREATE POLICY "Service role can update videos"
ON storage.objects FOR UPDATE
TO service_role
USING (bucket_id = 'videos');

-- Policy: Allow service role to delete files
CREATE POLICY "Service role can delete videos"
ON storage.objects FOR DELETE
TO service_role
USING (bucket_id = 'videos');
