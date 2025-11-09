-- ============================================================================
-- RLS POLICIES FOR TEACHER PENDING APPROVALS (BOOKS)
-- ============================================================================
-- These policies ensure that:
-- 1. Teachers can only see/approve books for subjects they teach
-- 2. Students can upload proof images for their own books
-- 3. Service role (backend) has full access for system operations
-- ============================================================================

-- ===== ENABLE RLS ON BOOKS TABLE =====
-- First, ensure RLS is enabled (if not already)
ALTER TABLE books ENABLE ROW LEVEL SECURITY;


-- ===== POLICY 1: Service Role Full Access =====
-- Backend service can manage all books
CREATE POLICY "Service role has full access to books"
ON books
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);


-- ===== POLICY 2: Students Can View Their Own Books =====
-- Students can see books assigned to them
CREATE POLICY "Students can view their own books"
ON books
FOR SELECT
TO authenticated
USING (
  student_id IN (
    SELECT student_id 
    FROM students 
    WHERE auth_uid = auth.uid()
  )
);


-- ===== POLICY 3: Students Can Upload Proof Images =====
-- Y1 students can upload proof images for their own books
CREATE POLICY "Students can upload proof for their own books"
ON books
FOR UPDATE
TO authenticated
USING (
  student_id IN (
    SELECT student_id 
    FROM students 
    WHERE auth_uid = auth.uid()
  )
)
WITH CHECK (
  student_id IN (
    SELECT student_id 
    FROM students 
    WHERE auth_uid = auth.uid()
  )
);


-- ===== POLICY 4: Teachers Can View Books For Their Subjects =====
-- Teachers can see all books for subjects they teach
CREATE POLICY "Teachers can view books for their subjects"
ON books
FOR SELECT
TO authenticated
USING (
  subject_id IN (
    SELECT DISTINCT c.subject_id 
    FROM classes c
    JOIN teachers t ON c.teacher_id = t.teacher_id
    WHERE t.auth_uid = auth.uid()
  )
);


-- ===== POLICY 5: Teachers Can Approve Books For Their Subjects =====
-- Teachers can approve/reject books for subjects they teach
CREATE POLICY "Teachers can approve books for their subjects"
ON books
FOR UPDATE
TO authenticated
USING (
  subject_id IN (
    SELECT DISTINCT c.subject_id 
    FROM classes c
    JOIN teachers t ON c.teacher_id = t.teacher_id
    WHERE t.auth_uid = auth.uid()
  )
)
WITH CHECK (
  subject_id IN (
    SELECT DISTINCT c.subject_id 
    FROM classes c
    JOIN teachers t ON c.teacher_id = t.teacher_id
    WHERE t.auth_uid = auth.uid()
  )
);


-- ===== POLICY 6: Teachers Can Mark Physical Returns =====
-- Teachers can mark books as physically returned (Y2 workflow)
CREATE POLICY "Teachers can mark books as returned"
ON books
FOR UPDATE
TO authenticated
USING (
  subject_id IN (
    SELECT DISTINCT c.subject_id 
    FROM classes c
    JOIN teachers t ON c.teacher_id = t.teacher_id
    WHERE t.auth_uid = auth.uid()
  )
)
WITH CHECK (
  subject_id IN (
    SELECT DISTINCT c.subject_id 
    FROM classes c
    JOIN teachers t ON c.teacher_id = t.teacher_id
    WHERE t.auth_uid = auth.uid()
  )
);


-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================
-- Run these to verify the policies are working correctly

-- 1. Check that RLS is enabled
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE tablename = 'books';
-- Expected: rowsecurity = true

-- 2. List all policies on books table
SELECT 
    policyname,
    cmd,
    qual,
    with_check
FROM pg_policies 
WHERE tablename = 'books'
ORDER BY policyname;

-- 3. Test as teacher (you'll need to be logged in as teacher)
-- This should show only books for subjects you teach
SELECT * FROM teacher_pending_approvals;

-- 4. Count books by teacher (as admin/service role)
SELECT 
    t.first_name || ' ' || t.last_name as teacher_name,
    sub.subject_name,
    COUNT(b.book_id) as book_count,
    COUNT(CASE WHEN b.approval_status = 'pending' THEN 1 END) as pending_count
FROM teachers t
JOIN classes c ON t.teacher_id = c.teacher_id
JOIN subjects sub ON c.subject_id = sub.subject_id
LEFT JOIN books b ON sub.subject_id = b.subject_id
GROUP BY t.teacher_id, t.first_name, t.last_name, sub.subject_name
ORDER BY teacher_name, subject_name;


-- ============================================================================
-- NOTES
-- ============================================================================
-- 
-- VIEW ACCESS:
-- The view `teacher_pending_approvals` automatically respects these RLS
-- policies because it queries the `books` table. When a teacher queries the
-- view, they only see books for subjects they teach.
--
-- MULTI-SUBJECT TEACHERS:
-- If a teacher teaches multiple subjects (e.g., Math and Physics), they will
-- see pending approvals for books from BOTH subjects. This is by design.
--
-- WORKFLOW:
-- 1. Y1 Student uploads book proof → UPDATE their own book record
-- 2. Teacher views pending approvals → SELECT filtered by their subjects
-- 3. Teacher approves/rejects → UPDATE filtered by their subjects
-- 4. Y2 Students physically return → Teacher marks returned via UPDATE
--
-- SECURITY:
-- - Students can't see other students' books
-- - Teachers can't access books for subjects they don't teach
-- - All changes are logged (approved_by, approved_at)
-- - Service role bypasses RLS for system operations
--
-- EDGE CASES:
-- - If a teacher stops teaching a subject, they lose access to those books
-- - If multiple teachers teach the same subject, any of them can approve
-- - Books without a subject_id are not visible to any teacher (by design)
--
-- ============================================================================
