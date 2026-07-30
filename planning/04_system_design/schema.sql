CREATE TABLE analyses (
  id UUID PRIMARY KEY,
  status TEXT NOT NULL CHECK (status IN ('queued','extracting','review','diagnosing','complete','failed')),
  template_id TEXT NOT NULL,
  demo_mode BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  error_code TEXT
);

CREATE TABLE students (
  id UUID PRIMARY KEY,
  analysis_id UUID NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
  display_label TEXT NOT NULL,
  external_identifier TEXT,
  UNIQUE (analysis_id, display_label)
);

CREATE TABLE items (
  id UUID PRIMARY KEY,
  analysis_id UUID NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
  item_key TEXT NOT NULL,
  problem_json JSONB NOT NULL,
  form TEXT NOT NULL CHECK (form IN ('bare','word')),
  held_out BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE readings (
  id UUID PRIMARY KEY,
  student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
  candidates_json JSONB NOT NULL,
  selected_answer TEXT,
  step_features JSONB NOT NULL DEFAULT '[]',
  ocr_confidence DOUBLE PRECISION,
  teacher_reviewed BOOLEAN NOT NULL DEFAULT FALSE,
  crop_object_key TEXT,
  UNIQUE (student_id, item_id)
);

CREATE TABLE diagnoses (
  id UUID PRIMARY KEY,
  student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  engine_version TEXT NOT NULL,
  posterior_json JSONB NOT NULL,
  top_hypothesis TEXT,
  confidence_state TEXT NOT NULL,
  action_category TEXT NOT NULL,
  evidence_json JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE diagnostic_items (
  id UUID PRIMARY KEY,
  diagnosis_id UUID NOT NULL REFERENCES diagnoses(id) ON DELETE CASCADE,
  rank INTEGER NOT NULL,
  problem_json JSONB NOT NULL,
  information_gain DOUBLE PRECISION NOT NULL,
  separation_json JSONB NOT NULL
);

CREATE TABLE evaluation_runs (
  id UUID PRIMARY KEY,
  dataset_name TEXT NOT NULL,
  dataset_type TEXT NOT NULL,
  engine_version TEXT NOT NULL,
  metrics_json JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
