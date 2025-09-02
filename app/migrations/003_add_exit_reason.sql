-- Migration: Add exit_reason column to trades table
-- Date: 2024-01-XX

-- Check if column doesn't exist before adding it
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'trades' AND column_name = 'exit_reason') THEN
        ALTER TABLE trades ADD COLUMN exit_reason VARCHAR(50) NULL;

        -- Add comment to document the column
        COMMENT ON COLUMN trades.exit_reason IS 'Reason for trade exit: manual, take_profit, or stop_loss';
    END IF;
END $$;
