/*
  # Create Email Recipients Table for Automated Reports

  1. New Tables
    - `email_recipients`
      - `id` (uuid, primary key) - Unique recipient identifier
      - `email` (text) - Email address
      - `name` (text) - Recipient name
      - `role` (text) - Role (PM, Admin, etc.)
      - `active` (boolean) - Whether recipient is active
      - `report_types` (text[]) - Types of reports to receive
      - `created_at` (timestamptz) - Creation timestamp
      - `updated_at` (timestamptz) - Last update timestamp

    - `email_logs`
      - `id` (uuid, primary key) - Unique log identifier
      - `recipient_email` (text) - Email sent to
      - `subject` (text) - Email subject
      - `report_date` (date) - Report date
      - `attachment_name` (text) - Attachment filename
      - `status` (text) - sent, failed, pending
      - `error_message` (text) - Error details if failed
      - `sent_at` (timestamptz) - Timestamp when sent

  2. Security
    - Enable RLS on both tables
    - Only Admin can manage recipients
    - Service role for automated sending

  3. Indexes
    - Index on email for fast lookups
    - Index on active status
    - Index on sent_at for logs
*/

-- Create email_recipients table
CREATE TABLE IF NOT EXISTS email_recipients (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text UNIQUE NOT NULL,
  name text NOT NULL,
  role text DEFAULT 'PM',
  active boolean DEFAULT true,
  report_types text[] DEFAULT ARRAY['daily'],
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create email_logs table
CREATE TABLE IF NOT EXISTS email_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  recipient_email text NOT NULL,
  subject text NOT NULL,
  report_date date NOT NULL,
  attachment_name text,
  status text NOT NULL DEFAULT 'pending',
  error_message text,
  sent_at timestamptz DEFAULT now()
);

-- Enable RLS
ALTER TABLE email_recipients ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_logs ENABLE ROW LEVEL SECURITY;

-- Policies for email_recipients (Admin only)
CREATE POLICY "Admin can manage email recipients"
  ON email_recipients
  FOR ALL
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM auth.users
      WHERE auth.users.id = auth.uid()
      AND auth.users.raw_user_meta_data->>'role' = 'admin'
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM auth.users
      WHERE auth.users.id = auth.uid()
      AND auth.users.raw_user_meta_data->>'role' = 'admin'
    )
  );

-- Service role can manage all recipients
CREATE POLICY "Service role can manage recipients"
  ON email_recipients
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Policies for email_logs (Admin can view)
CREATE POLICY "Admin can view email logs"
  ON email_logs
  FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM auth.users
      WHERE auth.users.id = auth.uid()
      AND auth.users.raw_user_meta_data->>'role' = 'admin'
    )
  );

-- Service role can manage all logs
CREATE POLICY "Service role can manage logs"
  ON email_logs
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_email_recipients_email ON email_recipients(email);
CREATE INDEX IF NOT EXISTS idx_email_recipients_active ON email_recipients(active);
CREATE INDEX IF NOT EXISTS idx_email_logs_sent_at ON email_logs(sent_at DESC);
CREATE INDEX IF NOT EXISTS idx_email_logs_status ON email_logs(status);
CREATE INDEX IF NOT EXISTS idx_email_logs_report_date ON email_logs(report_date DESC);

-- Create trigger for updated_at
DROP TRIGGER IF EXISTS update_email_recipients_updated_at ON email_recipients;
CREATE TRIGGER update_email_recipients_updated_at
    BEFORE UPDATE ON email_recipients
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert default recipients (examples - update with actual emails)
INSERT INTO email_recipients (email, name, role, active, report_types)
VALUES
  ('pm1@example.com', 'Project Manager 1', 'PM', false, ARRAY['daily']),
  ('pm2@example.com', 'Project Manager 2', 'PM', false, ARRAY['daily', 'weekly'])
ON CONFLICT (email) DO NOTHING;
