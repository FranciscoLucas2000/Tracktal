CREATE TABLE job_skills (
  job_id UUID NOT NULL REFERENCES job_postings(id) ON DELETE CASCADE,
  skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
  PRIMARY KEY (job_id, skill_id)
);

CREATE INDEX job_skills_skill_id_idx ON job_skills (skill_id);

ALTER TABLE job_skills ENABLE ROW LEVEL SECURITY;

CREATE POLICY "authenticated_read" ON job_skills
  FOR SELECT USING (auth.role() = 'authenticated');
