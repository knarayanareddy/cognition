-- CLB Database Schema (derived from F-07 privacy-policy.md)
-- PostgreSQL — stores only derived signals, never raw content

-- Cognitive load scores time series
CREATE TABLE IF NOT EXISTS cl_scores (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID NOT NULL,
  score         INTEGER NOT NULL CHECK (score BETWEEN 0 AND 100),
  band          VARCHAR(20) NOT NULL,
  burnout_risk  DECIMAL(4,3),
  flow_state    BOOLEAN DEFAULT FALSE,
  component_scores JSONB,
  risk_factors  JSONB,
  recommended_interventions JSONB,
  data_mode     VARCHAR(10) DEFAULT 'live',
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Intervention log
CREATE TABLE IF NOT EXISTS interventions (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL,
  int_type        VARCHAR(10) NOT NULL,
  execution_mode  VARCHAR(10) NOT NULL,
  triggered_by    JSONB,
  cl_score_before INTEGER,
  cl_score_after  INTEGER,
  action_taken    TEXT,
  outcome         VARCHAR(20),
  miro_card_id    VARCHAR(100),
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Signal snapshots (derived only — no raw content per F-07)
CREATE TABLE IF NOT EXISTS signal_snapshots (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID NOT NULL,
  signal_id   VARCHAR(10) NOT NULL,
  value       DECIMAL(10,3),
  source_mode VARCHAR(10),
  captured_at TIMESTAMPTZ DEFAULT NOW()
);

-- User consent records (AC08: consent before data collection)
CREATE TABLE IF NOT EXISTS user_consent (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID UNIQUE NOT NULL,
  consent_level VARCHAR(10) NOT NULL,
  granted_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);

-- OAuth tokens (securely stored)
CREATE TABLE IF NOT EXISTS user_tokens (
  id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id              UUID UNIQUE NOT NULL,
  google_access_token  TEXT NOT NULL,
  google_refresh_token TEXT,
  token_expiry         TIMESTAMPTZ,
  created_at           TIMESTAMPTZ DEFAULT NOW(),
  updated_at           TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_cl_scores_user_id ON cl_scores(user_id);
CREATE INDEX IF NOT EXISTS idx_cl_scores_created_at ON cl_scores(created_at);
CREATE INDEX IF NOT EXISTS idx_interventions_user_id ON interventions(user_id);
CREATE INDEX IF NOT EXISTS idx_signal_snapshots_user_id ON signal_snapshots(user_id);
CREATE INDEX IF NOT EXISTS idx_signal_snapshots_captured_at ON signal_snapshots(captured_at);
