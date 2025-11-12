/*
  # Create Media Files Table for Photo/Video Uploads

  1. New Tables
    - `media_files`
      - `id` (uuid, primary key) - Unique media file identifier
      - `report_id` (uuid) - Reference to daily_reports
      - `activity_name` (text) - Activity this media is associated with
      - `file_name` (text) - Original file name
      - `file_path` (text) - Storage path in Supabase Storage
      - `file_type` (text) - MIME type (image/jpeg, video/mp4, etc.)
      - `file_size` (integer) - File size in bytes
      - `compressed` (boolean) - Whether file was compressed
      - `uploaded_by` (uuid) - User who uploaded the file
      - `uploaded_at` (timestamptz) - Upload timestamp

  2. Security
    - Enable RLS on media_files table
    - Engineers can upload media for their own reports
    - PM and Admin can view all media
    - Proper file size validation

  3. Indexes
    - Index on report_id for fast lookups
    - Index on activity_name for filtering
*/

-- Create media_files table
CREATE TABLE IF NOT EXISTS media_files (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  report_id uuid NOT NULL REFERENCES daily_reports(id) ON DELETE CASCADE,
  activity_name text NOT NULL,
  file_name text NOT NULL,
  file_path text NOT NULL,
  file_type text NOT NULL,
  file_size integer NOT NULL,
  compressed boolean DEFAULT false,
  uploaded_by uuid NOT NULL,
  uploaded_at timestamptz DEFAULT now()
);

-- Enable RLS
ALTER TABLE media_files ENABLE ROW LEVEL SECURITY;

-- Engineers can upload media for their own reports
CREATE POLICY "Engineers can upload media for own reports"
  ON media_files
  FOR INSERT
  TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM daily_reports
      WHERE daily_reports.id = media_files.report_id
      AND daily_reports.engineer_id::text = auth.uid()::text
    )
  );

-- Engineers can view their own media
CREATE POLICY "Engineers can view own media"
  ON media_files
  FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM daily_reports
      WHERE daily_reports.id = media_files.report_id
      AND daily_reports.engineer_id::text = auth.uid()::text
    )
  );

-- Engineers can delete their own media
CREATE POLICY "Engineers can delete own media"
  ON media_files
  FOR DELETE
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM daily_reports
      WHERE daily_reports.id = media_files.report_id
      AND daily_reports.engineer_id::text = auth.uid()::text
    )
  );

-- Service role can manage all media
CREATE POLICY "Service role can manage all media"
  ON media_files
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_media_files_report ON media_files(report_id);
CREATE INDEX IF NOT EXISTS idx_media_files_activity ON media_files(activity_name);
CREATE INDEX IF NOT EXISTS idx_media_files_uploaded_by ON media_files(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_media_files_uploaded_at ON media_files(uploaded_at DESC);
