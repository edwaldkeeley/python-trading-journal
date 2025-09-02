-- Migration: Add stop_loss and take_profit columns to trades table
-- Date: 2024

-- Add stop_loss column
ALTER TABLE trades ADD COLUMN IF NOT EXISTS stop_loss DOUBLE PRECISION NULL CHECK (stop_loss > 0);

-- Add take_profit column
ALTER TABLE trades ADD COLUMN IF NOT EXISTS take_profit DOUBLE PRECISION NULL CHECK (take_profit > 0);

-- Add comments for documentation
COMMENT ON COLUMN trades.stop_loss IS 'Stop loss price for risk management';
COMMENT ON COLUMN trades.take_profit IS 'Take profit target price';
