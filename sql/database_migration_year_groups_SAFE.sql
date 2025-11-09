-- ============================================================================
-- ECLARI DATABASE MIGRATION: Year Group Differentiated Clearance Workflow
-- SAFE VERSION - With error checking and rollback support
-- ============================================================================
-- This migration adds support for different clearance workflows:
-- - Y1 (Year 1): Students submit photo proof, teachers approve/reject
-- - Y2 (Year 2): Students physically return items, teachers mark as returned
--
-- New Features:
-- 1. Year group tracking on classes (for timetable color blocks)
-- 2. Image proof storage for Y1 student submissions
-- 3. Approval workflow (pending, approved, rejected)
-- 4. Timetable color block assignment per class
-- ============================================================================

-- Start transaction - will rollback if any error occurs
BEGIN;

-- ===== PRE-FLIGHT CHECKS =====
-- Verify required tables exist

DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'classes') THEN
        RAISE EXCEPTION 'Table "classes" does not exist. Cannot proceed with migration.';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'books') THEN
        RAISE EXCEPTION 'Table "books" does not exist. Cannot proceed with migration.';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'materials') THEN
        RAISE EXCEPTION 'Table "materials" does not exist. Cannot proceed with migration.';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'students') THEN
        RAISE EXCEPTION 'Table "students" does not exist. Cannot proceed with migration.';
    END IF;
    
    RAISE NOTICE 'Pre-flight checks passed. All required tables exist.';
END $$;


-- ===== STEP 1: ALTER CLASSES TABLE =====
-- Adding year_group and color_block columns

DO $$ 
BEGIN
    -- Add year_group column (1 or 2)
    ALTER TABLE classes 
    ADD COLUMN IF NOT EXISTS year_group INT CHECK (year_group IN (1, 2));
    
    RAISE NOTICE '✓ Added year_group column to classes';
    
    -- Add color_block for timetable visualization
    ALTER TABLE classes 
    ADD COLUMN IF NOT EXISTS color_block TEXT CHECK (color_block IN ('green', 'yellow', 'blue', 'red', 'purple', 'orange'));
    
    RAISE NOTICE '✓ Added color_block column to classes';
END $$;

-- Add comments for documentation
COMMENT ON COLUMN classes.year_group IS 'Year group this class belongs to (1 or 2). Determines clearance workflow.';
COMMENT ON COLUMN classes.color_block IS 'Time slot identifier for block scheduling (green, yellow, blue, red, purple, orange). All students have the same color block at the same time but different subjects. E.g., Yellow Block = 9:30-11:00am for everyone.';


-- ===== STEP 2: ALTER BOOKS TABLE =====
-- Adding approval workflow columns for Y1 students

DO $$ 
BEGIN
    -- Add image_proof_url for Y1 student photo submissions
    ALTER TABLE books 
    ADD COLUMN IF NOT EXISTS image_proof_url TEXT;
    
    -- Add approval_status for teacher review workflow
    ALTER TABLE books 
    ADD COLUMN IF NOT EXISTS approval_status TEXT CHECK (approval_status IN ('pending', 'approved', 'rejected')) DEFAULT 'pending';
    
    -- Add approved_by to track which teacher approved (no FK constraint for flexibility)
    ALTER TABLE books 
    ADD COLUMN IF NOT EXISTS approved_by TEXT;
    
    -- Add approval timestamp
    ALTER TABLE books 
    ADD COLUMN IF NOT EXISTS approved_at TIMESTAMPTZ;
    
    -- Add rejection reason for feedback to students
    ALTER TABLE books 
    ADD COLUMN IF NOT EXISTS rejection_reason TEXT;
    
    -- Add submitted_at timestamp for when Y1 student uploads proof
    ALTER TABLE books 
    ADD COLUMN IF NOT EXISTS submitted_at TIMESTAMPTZ;
    
    RAISE NOTICE '✓ Added 6 new columns to books table';
END $$;

-- Add comments
COMMENT ON COLUMN books.image_proof_url IS 'URL to uploaded image proof for Y1 students (stored in Supabase Storage)';
COMMENT ON COLUMN books.approval_status IS 'Approval workflow status: pending (waiting for teacher), approved (cleared), rejected (needs resubmission)';
COMMENT ON COLUMN books.approved_by IS 'Teacher ID who approved/rejected the submission (stored as TEXT)';
COMMENT ON COLUMN books.approved_at IS 'Timestamp when teacher approved/rejected';
COMMENT ON COLUMN books.rejection_reason IS 'Reason for rejection (shown to student for resubmission)';
COMMENT ON COLUMN books.submitted_at IS 'Timestamp when Y1 student uploaded proof image';


-- ===== STEP 3: ALTER MATERIALS TABLE =====
-- Adding approval workflow columns for materials

DO $$ 
BEGIN
    -- Add image_proof_url for Y1 student photo submissions (lab/sports items)
    ALTER TABLE materials 
    ADD COLUMN IF NOT EXISTS image_proof_url TEXT;
    
    -- Add approval_status for teacher/staff review workflow
    ALTER TABLE materials 
    ADD COLUMN IF NOT EXISTS approval_status TEXT CHECK (approval_status IN ('pending', 'approved', 'rejected')) DEFAULT 'pending';
    
    -- Add approved_by to track which staff member approved
    ALTER TABLE materials 
    ADD COLUMN IF NOT EXISTS approved_by TEXT;
    
    -- Add approval timestamp
    ALTER TABLE materials 
    ADD COLUMN IF NOT EXISTS approved_at TIMESTAMPTZ;
    
    -- Add rejection reason
    ALTER TABLE materials 
    ADD COLUMN IF NOT EXISTS rejection_reason TEXT;
    
    -- Add submitted_at timestamp
    ALTER TABLE materials 
    ADD COLUMN IF NOT EXISTS submitted_at TIMESTAMPTZ;
    
    RAISE NOTICE '✓ Added 6 new columns to materials table';
END $$;

-- Add comments
COMMENT ON COLUMN materials.image_proof_url IS 'URL to uploaded image proof for Y1 students (for non-physical return items)';
COMMENT ON COLUMN materials.approval_status IS 'Approval workflow status: pending, approved, rejected';
COMMENT ON COLUMN materials.approved_by IS 'Staff ID (lab_staff_id or coach_id) who approved/rejected';
COMMENT ON COLUMN materials.approved_at IS 'Timestamp when staff approved/rejected';
COMMENT ON COLUMN materials.rejection_reason IS 'Reason for rejection (feedback for student)';
COMMENT ON COLUMN materials.submitted_at IS 'Timestamp when Y1 student uploaded proof image';


-- ===== STEP 4: UPDATE EXISTING DATA =====
-- Setting defaults for existing records

DO $$ 
BEGIN
    -- Update students year_group if not already set (based on existing data patterns)
    UPDATE students 
    SET year_group = 1 
    WHERE year_group IS NULL AND student_id LIKE 'STU_1%';
    
    UPDATE students 
    SET year_group = 2 
    WHERE year_group IS NULL AND student_id LIKE 'STU_2%';
    
    -- Set default year_group for any remaining students
    UPDATE students 
    SET year_group = 1 
    WHERE year_group IS NULL;
    
    RAISE NOTICE '✓ Updated student year_groups';
    
    -- Update classes to have year_groups
    UPDATE classes 
    SET year_group = 1 
    WHERE year_group IS NULL AND class_id LIKE '%Y1%';
    
    UPDATE classes 
    SET year_group = 2 
    WHERE year_group IS NULL AND class_id LIKE '%Y2%';
    
    -- Set default year_group = 1 for classes without year_group
    UPDATE classes 
    SET year_group = 1 
    WHERE year_group IS NULL;
    
    RAISE NOTICE '✓ Updated class year_groups';
    
    -- Assign default color blocks to existing classes
    -- Note: Color blocks represent time slots, not subject categories
    UPDATE classes 
    SET color_block = CASE 
        WHEN class_id LIKE '%_1' OR class_id LIKE '%_A' THEN 'green'   -- Period 1
        WHEN class_id LIKE '%_2' OR class_id LIKE '%_B' THEN 'yellow'  -- Period 2
        WHEN class_id LIKE '%_3' OR class_id LIKE '%_C' THEN 'blue'    -- Period 3
        WHEN class_id LIKE '%_4' OR class_id LIKE '%_D' THEN 'red'     -- Period 4
        WHEN class_id LIKE '%_5' OR class_id LIKE '%_E' THEN 'purple'  -- Period 5
        ELSE 'orange'  -- Evening/optional period
    END
    WHERE color_block IS NULL;
    
    RAISE NOTICE '✓ Assigned color blocks to classes';
    
    -- For Y2 students with existing returned books, set approval_status to 'approved'
    UPDATE books 
    SET approval_status = 'approved', 
        approved_at = NOW()
    WHERE returned = true 
      AND student_id IN (SELECT student_id FROM students WHERE year_group = 2);
    
    -- Same for materials
    UPDATE materials 
    SET approval_status = 'approved', 
        approved_at = NOW()
    WHERE returned = true 
      AND student_id IN (SELECT student_id FROM students WHERE year_group = 2);
    
    RAISE NOTICE '✓ Set approval_status for existing Y2 returns';
END $$;


-- ===== STEP 5: CREATE INDEXES FOR PERFORMANCE =====
-- Speed up common queries

DO $$ 
BEGIN
    CREATE INDEX IF NOT EXISTS idx_books_approval_status ON books(approval_status);
    CREATE INDEX IF NOT EXISTS idx_books_student_approval ON books(student_id, approval_status);
    CREATE INDEX IF NOT EXISTS idx_materials_approval_status ON materials(approval_status);
    CREATE INDEX IF NOT EXISTS idx_materials_student_approval ON materials(student_id, approval_status);
    CREATE INDEX IF NOT EXISTS idx_classes_year_group ON classes(year_group);
    CREATE INDEX IF NOT EXISTS idx_classes_color_block ON classes(color_block);
    CREATE INDEX IF NOT EXISTS idx_students_year_group ON students(year_group);
    
    RAISE NOTICE '✓ Created 7 performance indexes';
END $$;


-- ===== STEP 6: CREATE HELPFUL VIEWS =====
-- Views to make querying easier

DO $$ 
BEGIN
    -- Note: Views must be created outside of transaction blocks
    -- These are created with CREATE OR REPLACE which handles existing views
    RAISE NOTICE 'Step 6: Creating helper views...';
END $$;

-- View: Pending approvals for teachers
CREATE OR REPLACE VIEW teacher_pending_approvals AS
SELECT 
    b.book_id,
    b.student_id,
    s.first_name || ' ' || s.last_name as student_name,
    s.year_group,
    b.book_name,
    sub.subject_name,
    b.image_proof_url,
    b.submitted_at,
    b.approval_status,
    c.teacher_id,
    c.color_block
FROM books b
JOIN students s ON b.student_id = s.student_id
JOIN subjects sub ON b.subject_id = sub.subject_id
JOIN classes c ON c.subject_id = sub.subject_id
WHERE s.year_group = 1 
  AND b.image_proof_url IS NOT NULL 
  AND b.approval_status = 'pending';

-- View: Pending material approvals for lab/coach staff
CREATE OR REPLACE VIEW staff_pending_material_approvals AS
SELECT 
    m.material_id,
    m.student_id,
    s.first_name || ' ' || s.last_name as student_name,
    s.year_group,
    m.material_name,
    m.subject_id,
    m.image_proof_url,
    m.submitted_at,
    m.approval_status
FROM materials m
JOIN students s ON m.student_id = s.student_id
WHERE s.year_group = 1 
  AND m.image_proof_url IS NOT NULL 
  AND m.approval_status = 'pending';

DO $$ 
BEGIN
    RAISE NOTICE '✓ Created 2 helper views';
END $$;


-- ===== COMMIT TRANSACTION =====
DO $$ 
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Migration completed successfully!';
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '1. Create storage bucket: clearance-proofs';
    RAISE NOTICE '2. Set up RLS policies for storage bucket';
    RAISE NOTICE '3. Run verification queries below';
    RAISE NOTICE '';
END $$;

COMMIT;


-- ===== VERIFICATION QUERIES =====
-- Run these separately AFTER the migration completes

-- Check classes with year groups and color blocks
SELECT class_id, year_group, color_block 
FROM classes 
LIMIT 5;

-- Check books with new approval columns
SELECT book_id, student_id, book_name, approval_status, image_proof_url, submitted_at
FROM books 
LIMIT 5;

-- Check materials with new approval columns
SELECT material_id, student_id, material_name, approval_status, image_proof_url, submitted_at
FROM materials 
LIMIT 5;

-- Count students by year group
SELECT year_group, COUNT(*) as student_count
FROM students
GROUP BY year_group
ORDER BY year_group;

-- Count classes by color block
SELECT color_block, COUNT(*) as class_count
FROM classes
GROUP BY color_block
ORDER BY color_block;

-- Count pending approvals
SELECT 
    'Books' as item_type,
    COUNT(*) as pending_count
FROM books
WHERE approval_status = 'pending' AND image_proof_url IS NOT NULL
UNION ALL
SELECT 
    'Materials' as item_type,
    COUNT(*) as pending_count
FROM materials
WHERE approval_status = 'pending' AND image_proof_url IS NOT NULL;


-- ============================================================================
-- MIGRATION COMPLETE!
-- ============================================================================
-- If you see this message, all changes were applied successfully.
-- 
-- RLS POLICIES NOTE:
-- The original script had RLS policies, but they may conflict with existing
-- policies. If you need RLS policies, add them manually after testing:
--
-- 1. Go to Supabase Dashboard > Authentication > Policies
-- 2. Select the books table
-- 3. Add UPDATE policy for students (their own records)
-- 4. Add UPDATE policy for teachers (their subject's records)
-- 5. Repeat for materials table
-- ============================================================================
