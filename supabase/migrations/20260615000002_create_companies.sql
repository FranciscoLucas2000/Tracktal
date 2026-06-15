CREATE TABLE companies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  website TEXT,
  sector TEXT,
  country TEXT CHECK (country IN ('PT', 'ES')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX companies_name_lower_idx ON companies (lower(name));
CREATE INDEX companies_country_idx ON companies (country);

ALTER TABLE companies ENABLE ROW LEVEL SECURITY;

CREATE POLICY "authenticated_read" ON companies
  FOR SELECT USING (auth.role() = 'authenticated');
