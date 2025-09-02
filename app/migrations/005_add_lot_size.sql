-- Migration: Add lot_size column to trades table
-- Date: 2024-01-XX

-- Check if column doesn't exist before adding it
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'trades' AND column_name = 'lot_size') THEN
        ALTER TABLE trades ADD COLUMN lot_size DOUBLE PRECISION NOT NULL DEFAULT 1 CHECK (lot_size > 0);
        COMMENT ON COLUMN trades.lot_size IS 'Lot size multiplier (e.g., 100 for standard lots)';
    END IF;
END $$;
