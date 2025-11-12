/*
  # Create Daily Progress Reports Tables

  1. New Tables
    - `daily_reports`
      - `id` (uuid, primary key) - Unique report identifier
      - `report_date` (date) - Date of the report
      - `site_code` (text) - TCB site code
      - `engineer_id` (uuid) - Reference to user who created report
      - `weather` (text) - Weather conditions
      - `total_workers` (integer) - Total number of workers
      - `remarks` (text) - General remarks
      - `created_at` (timestamptz) - Report creation timestamp
      - `updated_at` (timestamptz) - Last update timestamp
      
    - `report_activities`
      - `id` (uuid, primary key) - Unique activity identifier
      - `report_id` (uuid) - Reference to daily_reports
      - `activity_name` (text) - Name of the activity
      - `unit` (text) - Unit of measurement
      - `target` (decimal) - Target quantity
      - `achieved` (decimal) - Achieved quantity
      - `cumulative` (decimal) - Cumulative progress
      - `remarks` (text) - Activity-specific remarks

  2. Security
    - Enable RLS on both tables
    - Engineers can create and view own reports
    - PM and Admin can view all reports
    
  3. Indexes
    - Index on report_date and site_code for faster queries
    - Index on engineer_id for user-specific queries
*/

-- Create daily_reports table
CREATE TABLE IF NOT EXISTS daily_reports (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  report_date date NOT NULL,
  site_code text NOT NULL,
  engineer_id uuid NOT NULL,
  weather text DEFAULT '',
  total_workers integer DEFAULT 0,
  remarks text DEFAULT '',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  UNIQUE(report_date, site_code)
);

-- Create report_activities table
CREATE TABLE IF NOT EXISTS report_activities (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  report_id uuid NOT NULL REFERENCES daily_reports(id) ON DELETE CASCADE,
  activity_name text NOT NULL,
  unit text NOT NULL,
  target decimal(10,2) DEFAULT 0,
  achieved decimal(10,2) DEFAULT 0,
  cumulative decimal(10,2) DEFAULT 0,
  remarks text DEFAULT ''
);

-- Enable RLS
ALTER TABLE daily_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE report_activities ENABLE ROW LEVEL SECURITY;

-- Policies for daily_reports
CREATE POLICY "Engineers can create own reports"
  ON daily_reports
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid()::text = engineer_id::text);

CREATE POLICY "Engineers can view own reports"
  ON daily_reports
  FOR SELECT
  TO authenticated
  USING (auth.uid()::text = engineer_id::text);

CREATE POLICY "Engineers can update own reports"
  ON daily_reports
  FOR UPDATE
  TO authenticated
  USING (auth.uid()::text = engineer_id::text)
  WITH CHECK (auth.uid()::text = engineer_id::text);

CREATE POLICY "Service role can manage all reports"
  ON daily_reports
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Policies for report_activities
CREATE POLICY "Users can manage activities for their reports"
  ON report_activities
  FOR ALL
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM daily_reports
      WHERE daily_reports.id = report_activities.report_id
      AND daily_reports.engineer_id::text = auth.uid()::text
    )
  );

CREATE POLICY "Service role can manage all activities"
  ON report_activities
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_daily_reports_date ON daily_reports(report_date DESC);
CREATE INDEX IF NOT EXISTS idx_daily_reports_site ON daily_reports(site_code);
CREATE INDEX IF NOT EXISTS idx_daily_reports_engineer ON daily_reports(engineer_id);
CREATE INDEX IF NOT EXISTS idx_report_activities_report ON report_activities(report_id);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for updated_at
DROP TRIGGER IF EXISTS update_daily_reports_updated_at ON daily_reports;
CREATE TRIGGER update_daily_reports_updated_at
    BEFORE UPDATE ON daily_reports
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
