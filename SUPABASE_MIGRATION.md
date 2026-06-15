# Supabase Migration — SigRank Importer Overhaul

Run these in the Supabase SQL Editor (Dashboard → SQL Editor → New Query).

---

## 1. Add columns to `sigrank_operators`

```sql
-- Timestamp for when the entry was last submitted/updated
ALTER TABLE sigrank_operators
  ADD COLUMN IF NOT EXISTS submitted_at TIMESTAMPTZ DEFAULT now();

-- HuggingFace username — only authenticated users can persist
ALTER TABLE sigrank_operators
  ADD COLUMN IF NOT EXISTS hf_user TEXT;

-- Index for fast lookups by HF user
CREATE INDEX IF NOT EXISTS idx_sigrank_operators_hf_user
  ON sigrank_operators (hf_user);
```

---

## 2. Create `sigrank_sessions` table (session history / Greatest Hits)

```sql
CREATE TABLE IF NOT EXISTS sigrank_sessions (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name TEXT NOT NULL,
  input BIGINT NOT NULL DEFAULT 0,
  output BIGINT NOT NULL DEFAULT 0,
  cache_create BIGINT NOT NULL DEFAULT 0,
  cache_read BIGINT NOT NULL DEFAULT 0,
  cost_usd DOUBLE PRECISION,
  source TEXT DEFAULT 'manual',
  estimated BOOLEAN DEFAULT FALSE,
  caveat TEXT,
  hf_user TEXT,
  submitted_at TIMESTAMPTZ DEFAULT now()
);

-- Index for loading a user's session history
CREATE INDEX IF NOT EXISTS idx_sigrank_sessions_name
  ON sigrank_sessions (name, submitted_at DESC);
```

---

## 3. RLS policies (keep anon read-only, service key for writes)

```sql
-- Enable RLS on the new table
ALTER TABLE sigrank_sessions ENABLE ROW LEVEL SECURITY;

-- Anon can read session history
CREATE POLICY "anon_read_sessions" ON sigrank_sessions
  FOR SELECT USING (true);

-- Service role can insert (writes come from the app backend)
CREATE POLICY "service_insert_sessions" ON sigrank_sessions
  FOR INSERT WITH CHECK (true);

-- Same pattern for the new columns on sigrank_operators
-- (existing policies should already cover SELECT/INSERT;
--  verify the existing INSERT policy allows the new columns)
```

---

## 4. Verify

After running the above, check:

```sql
-- Should show submitted_at and hf_user columns
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'sigrank_operators'
ORDER BY ordinal_position;

-- Should exist with all columns
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'sigrank_sessions'
ORDER BY ordinal_position;
```

---

## Notes

- `sigrank_operators` still upserts on `name` (one board entry per operator)
- `sigrank_sessions` is append-only — every submission creates a new row
- The app reads sessions via `load_session_history(name, limit=5)` for the Greatest Hits display
- `hf_user` is populated only when the user is authenticated via HuggingFace OAuth on the Space
- Without the `SUPABASE_SERVICE_KEY` env var, all writes are no-ops (safe for public demo)
