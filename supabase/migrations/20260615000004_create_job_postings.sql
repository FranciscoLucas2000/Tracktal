CREATE OR REPLACE FUNCTION trigger_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TABLE job_postings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source TEXT NOT NULL CHECK (source IN ('adzuna', 'indeed', 'linkedin', 'eures')),
  external_id TEXT NOT NULL,

  raw_title TEXT,
  raw_description TEXT,
  raw_location TEXT,
  raw_salary_min NUMERIC,
  raw_salary_max NUMERIC,
  raw_company_name TEXT,
  raw_posted_at TIMESTAMPTZ,

  normalised_title TEXT,
  title_category TEXT,
  company_id UUID REFERENCES companies(id),
  location_id UUID REFERENCES locations(id),
  salary_min_eur NUMERIC,
  salary_max_eur NUMERIC,
  salary_period TEXT CHECK (salary_period IN ('hourly', 'monthly', 'annual')),
  employment_type TEXT CHECK (employment_type IN ('full_time', 'part_time', 'contract', 'internship')),
  remote_type TEXT CHECK (remote_type IN ('on_site', 'hybrid', 'remote')),
  experience_level TEXT CHECK (experience_level IN ('junior', 'mid', 'senior', 'unspecified')),

  is_normalised BOOLEAN NOT NULL DEFAULT FALSE,
  scraped_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

  UNIQUE (source, external_id)
);

CREATE INDEX ON job_postings (source, scraped_at);
CREATE INDEX ON job_postings (is_normalised);
CREATE INDEX ON job_postings (company_id);
CREATE INDEX ON job_postings (location_id);

CREATE TRIGGER set_updated_at
  BEFORE UPDATE ON job_postings
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

ALTER TABLE job_postings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "authenticated_read" ON job_postings
  FOR SELECT USING (auth.role() = 'authenticated');
