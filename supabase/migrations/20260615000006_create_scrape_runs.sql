CREATE TABLE scrape_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source TEXT NOT NULL CHECK (source IN ('adzuna', 'indeed', 'linkedin', 'eures')),
  status TEXT NOT NULL DEFAULT 'running' CHECK (status IN ('running', 'success', 'failed')),
  started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  completed_at TIMESTAMPTZ,
  postings_found INT NOT NULL DEFAULT 0,
  postings_new INT NOT NULL DEFAULT 0,
  error_message TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX scrape_runs_source_started_at_idx ON scrape_runs (source, started_at DESC);
CREATE INDEX scrape_runs_failed_idx ON scrape_runs (status)
  WHERE status = 'failed';
