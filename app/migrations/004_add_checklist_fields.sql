-- Migration: Add checklist fields to trades table
-- Date: 2024-01-XX

-- Check if columns don't exist before adding them
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'trades' AND column_name = 'checklist_grade') THEN
        ALTER TABLE trades ADD COLUMN checklist_grade VARCHAR(3) NULL;
        COMMENT ON COLUMN trades.checklist_grade IS 'Trade quality grade: A+, A, B+, B, C+, C, D+, D, F';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'trades' AND column_name = 'checklist_score') THEN
        ALTER TABLE trades ADD COLUMN checklist_score INTEGER NULL CHECK (checklist_score >= 0 AND checklist_score <= 100);
        COMMENT ON COLUMN trades.checklist_score IS 'Trade quality score: 0-100';
    END IF;
END $$;

