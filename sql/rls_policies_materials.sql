-- ============================================================================
-- RLS POLICIES FOR STAFF PENDING MATERIAL APPROVALS
-- ============================================================================
-- These policies ensure that:
-- 1. Lab staff can only see/approve science materials (subject_id = 'SCI')
-- 2. Coaches can only see/approve PE materials (subject_id = 'PE')
-- 3. Students can upload proof images for their own materials
-- 4. Service role (backend) has full access for system operations
-- ============================================================================

-- ===== ENABLE RLS ON MATERIALS TABLE =====
-- First, ensure RLS is enabled (if not already)
ALTER TABLE materials ENABLE ROW LEVEL SECURITY;


-- ===== POLICY 1: Service Role Full Access =====
-- Backend service can manage all materials
CREATE POLICY "Service role has full access to materials"
ON materials
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);


-- ===== POLICY 2: Students Can View Their Own Materials =====
-- Students can see materials assigned to them
CREATE POLICY "Students can view their own materials"
ON materials
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
-- Y1 students can upload proof images for their own materials
CREATE POLICY "Students can upload proof for their own materials"
ON materials
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


-- ===== POLICY 4: Lab Staff Can View Science Materials =====
-- Lab staff can see all science (SCI) materials for approval workflow
CREATE POLICY "Lab staff can view science materials"
ON materials
FOR SELECT
TO authenticated
USING (
  subject_id = 'SCI' 
  AND EXISTS (
    SELECT 1 
    FROM lab_staff 
    WHERE lab_staff.auth_uid = auth.uid()
  )
);


-- ===== POLICY 5: Lab Staff Can Approve Science Materials =====
-- Lab staff can approve/reject science materials
CREATE POLICY "Lab staff can approve science materials"
ON materials
FOR UPDATE
TO authenticated
USING (
  subject_id = 'SCI' 
  AND EXISTS (
    SELECT 1 
    FROM lab_staff 
    WHERE lab_staff.auth_uid = auth.uid()
  )
)
WITH CHECK (
  subject_id = 'SCI' 
  AND EXISTS (
    SELECT 1 
    FROM lab_staff 
    WHERE lab_staff.auth_uid = auth.uid()
  )
);


-- ===== POLICY 6: Coaches Can View PE Materials =====
-- Coaches can see all PE materials for approval workflow
CREATE POLICY "Coaches can view PE materials"
ON materials
FOR SELECT
TO authenticated
USING (
  subject_id = 'PE' 
  AND EXISTS (
    SELECT 1 
    FROM coaches 
    WHERE coaches.auth_uid = auth.uid()
  )
);


-- ===== POLICY 7: Coaches Can Approve PE Materials =====
-- Coaches can approve/reject PE materials
CREATE POLICY "Coaches can approve PE materials"
ON materials
FOR UPDATE
TO authenticated
USING (
  subject_id = 'PE' 
  AND EXISTS (
    SELECT 1 
    FROM coaches 
    WHERE coaches.auth_uid = auth.uid()
  )
)
WITH CHECK (
  subject_id = 'PE' 
  AND EXISTS (
    SELECT 1 
    FROM coaches 
    WHERE coaches.auth_uid = auth.uid()
  )
);


-- ===== POLICY 8: Staff Can Mark Physical Returns =====
-- Lab staff and coaches can mark materials as physically returned
CREATE POLICY "Staff can mark materials as returned"
ON materials
FOR UPDATE
TO authenticated
USING (
  (
    subject_id = 'SCI' 
    AND EXISTS (SELECT 1 FROM lab_staff WHERE lab_staff.auth_uid = auth.uid())
  )
  OR
  (
    subject_id = 'PE' 
    AND EXISTS (SELECT 1 FROM coaches WHERE coaches.auth_uid = auth.uid())
  )
)
WITH CHECK (
  (
    subject_id = 'SCI' 
    AND EXISTS (SELECT 1 FROM lab_staff WHERE lab_staff.auth_uid = auth.uid())
  )
  OR
  (
    subject_id = 'PE' 
    AND EXISTS (SELECT 1 FROM coaches WHERE coaches.auth_uid = auth.uid())
  )
);


-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================
-- Run these to verify the policies are working correctly

-- 1. Check that RLS is enabled
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE tablename = 'materials';
-- Expected: rowsecurity = true

-- 2. List all policies on materials table
SELECT 
    policyname,
    cmd,
    qual,
    with_check
FROM pg_policies 
WHERE tablename = 'materials'
ORDER BY policyname;

-- 3. Test as lab staff (you'll need to be logged in as lab staff)
-- This should show only SCI materials
SELECT * FROM staff_pending_material_approvals;

-- 4. Test as coach (you'll need to be logged in as coach)
-- This should show only PE materials
SELECT * FROM staff_pending_material_approvals;


-- ============================================================================
-- NOTES
-- ============================================================================
-- 
-- VIEW ACCESS:
-- The view `staff_pending_material_approvals` automatically respects these
-- RLS policies because it queries the `materials` table. When a lab staff
-- member queries the view, they only see SCI materials. When a coach queries
-- the view, they only see PE materials.
--
-- WORKFLOW:
-- 1. Y1 Student uploads proof image → UPDATE their own material record
-- 2. Lab staff/Coach views pending approvals → SELECT filtered by subject_id
-- 3. Lab staff/Coach approves/rejects → UPDATE filtered by subject_id
-- 4. Y2 Students physically return → Staff marks returned via UPDATE
--
-- SECURITY:
-- - Students can't see other students' materials
-- - Lab staff can't access PE materials
-- - Coaches can't access SCI materials
-- - All changes are logged (approved_by, approved_at)
-- - Service role bypasses RLS for system operations
--
-- ============================================================================
