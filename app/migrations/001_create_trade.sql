CREATE TABLE IF NOT EXISTS trades (
  id BIGSERIAL PRIMARY KEY,
  symbol TEXT NOT NULL,
  side TEXT NOT NULL CHECK (side IN ('buy', 'sell')),
  quantity DOUBLE PRECISION NOT NULL CHECK (quantity > 0),
  entry_price DOUBLE PRECISION NOT NULL CHECK (entry_price > 0),
  entry_time TIMESTAMPTZ NOT NULL,
  exit_price DOUBLE PRECISION NULL CHECK (exit_price > 0),
  exit_time TIMESTAMPTZ NULL,
  fees DOUBLE PRECISION NOT NULL DEFAULT 0 CHECK (fees >= 0),
  notes TEXT NULL,
  pnl DOUBLE PRECISION NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
CREATE INDEX IF NOT EXISTS idx_trades_entry_time ON trades(entry_time DESC);

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_set_updated_at ON trades;
CREATE TRIGGER trg_set_updated_at
BEFORE UPDATE ON trades
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();