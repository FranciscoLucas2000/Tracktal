CREATE TABLE companies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  website TEXT,
  sector TEXT,
  country TEXT CHECK (country IN ('PT', 'ES')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE companies ENABLE ROW LEVEL SECURITY;

CREATE POLICY "authenticated_read" ON companies
  FOR SELECT USING (auth.role() = 'authenticated');
