CREATE TABLE locations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  city TEXT,
  region TEXT,
  country TEXT NOT NULL CHECK (country IN ('PT', 'ES')),
  lat NUMERIC(9,6),
  lng NUMERIC(9,6),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX locations_city_region_country_uidx
  ON locations (city, region, country)
  NULLS NOT DISTINCT;

CREATE INDEX locations_country_idx ON locations (country);

ALTER TABLE locations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "authenticated_read" ON locations
  FOR SELECT USING (auth.role() = 'authenticated');
