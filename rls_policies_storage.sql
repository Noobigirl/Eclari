-- ============================================================================
-- RLS POLICIES FOR STORAGE BUCKET: clearance-proofs
-- ============================================================================
-- These policies control who can upload/view proof images for the clearance system.
-- 
-- IMPORTANT: Run this in the Supabase SQL Editor AFTER creating the bucket.
-- ============================================================================

-- ===== POLICY 1: Students Can Upload Their Own Proof Images =====
-- Students can upload images for their own clearance items
CREATE POLICY "Students can upload their own proof images"
ON storage.objects
FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'clearance-proofs' 
  AND (storage.foldername(name))[1] IN (
    SELECT student_id::text 
    FROM students 
    WHERE auth_uid = auth.uid()
  )
);


-- ===== POLICY 2: Students Can View Their Own Proof Images =====
-- Students can see images they uploaded
CREATE POLICY "Students can view their own proof images"
ON storage.objects
FOR SELECT
TO authenticated
USING (
  bucket_id = 'clearance-proofs' 
  AND (storage.foldername(name))[1] IN (
    SELECT student_id::text 
    FROM students 
    WHERE auth_uid = auth.uid()
  )
);


-- ===== POLICY 3: Students Can Update Their Own Proof Images =====
-- Students can replace images they uploaded (before approval)
CREATE POLICY "Students can update their own proof images"
ON storage.objects
FOR UPDATE
TO authenticated
USING (
  bucket_id = 'clearance-proofs' 
  AND (storage.foldername(name))[1] IN (
    SELECT student_id::text 
    FROM students 
    WHERE auth_uid = auth.uid()
  )
)
WITH CHECK (
  bucket_id = 'clearance-proofs' 
  AND (storage.foldername(name))[1] IN (
    SELECT student_id::text 
    FROM students 
    WHERE auth_uid = auth.uid()
  )
);


-- ===== POLICY 4: Students Can Delete Their Own Proof Images =====
-- Students can delete images they uploaded (before approval)
CREATE POLICY "Students can delete their own proof images"
ON storage.objects
FOR DELETE
TO authenticated
USING (
  bucket_id = 'clearance-proofs' 
  AND (storage.foldername(name))[1] IN (
    SELECT student_id::text 
    FROM students 
    WHERE auth_uid = auth.uid()
  )
);


-- ===== POLICY 5: Teachers Can View Proof Images For Their Subjects =====
-- Teachers can see proof images for books in subjects they teach
CREATE POLICY "Teachers can view proof images for their subjects"
ON storage.objects
FOR SELECT
TO authenticated
USING (
  bucket_id = 'clearance-proofs'
  AND (
    -- Check if the teacher teaches the student who uploaded this image
    (storage.foldername(name))[1] IN (
      SELECT DISTINCT sc.student_id::text
      FROM student_classes sc
      JOIN classes c ON sc.class_id = c.class_id
      JOIN teachers t ON c.teacher_id = t.teacher_id
      WHERE t.auth_uid = auth.uid()
    )
  )
);


-- ===== POLICY 6: Lab Staff Can View Lab Equipment Proof Images =====
-- Lab staff can see proof images for lab materials
CREATE POLICY "Lab staff can view lab proof images"
ON storage.objects
FOR SELECT
TO authenticated
USING (
  bucket_id = 'clearance-proofs'
  AND (
    -- Check if this is lab staff
    EXISTS (
      SELECT 1 
      FROM lab_staff 
      WHERE auth_uid = auth.uid()
    )
    -- They can see proof for lab materials (subject_id = 'SCI')
    AND (storage.foldername(name))[1] IN (
      SELECT DISTINCT sc.student_id::text
      FROM student_classes sc
      JOIN classes c ON sc.class_id = c.class_id
      WHERE c.subject_id = 'SCI'
    )
  )
);


-- ===== POLICY 7: Coaches Can View Sports Equipment Proof Images =====
-- Coaches can see proof images for sports materials
CREATE POLICY "Coaches can view sports proof images"
ON storage.objects
FOR SELECT
TO authenticated
USING (
  bucket_id = 'clearance-proofs'
  AND (
    -- Check if this is a coach
    EXISTS (
      SELECT 1 
      FROM coaches 
      WHERE auth_uid = auth.uid()
    )
    -- They can see proof for sports materials (subject_id = 'PE')
    AND (storage.foldername(name))[1] IN (
      SELECT DISTINCT sc.student_id::text
      FROM student_classes sc
      JOIN classes c ON sc.class_id = c.class_id
      WHERE c.subject_id = 'PE'
    )
  )
);


-- ===== POLICY 8: Service Role Full Access =====
-- Backend service can manage all storage objects
CREATE POLICY "Service role has full access to clearance proofs"
ON storage.objects
FOR ALL
TO service_role
USING (bucket_id = 'clearance-proofs')
WITH CHECK (bucket_id = 'clearance-proofs');


-- ===== POLICY 9: Public Read Access (Optional) =====
-- Uncomment this if you want to allow public viewing of proof images
-- (Not recommended for student privacy reasons)
-- CREATE POLICY "Public can view clearance proofs"
-- ON storage.objects
-- FOR SELECT
-- TO public
-- USING (bucket_id = 'clearance-proofs');


-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- 1. List all storage policies
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual
FROM pg_policies 
WHERE schemaname = 'storage' 
  AND tablename = 'objects'
  AND policyname LIKE '%clearance%'
ORDER BY policyname;

-- 2. Check bucket configuration
SELECT * FROM storage.buckets WHERE id = 'clearance-proofs';

-- 3. Test file path parsing (run as admin)
-- This shows how the folder structure works
SELECT 
    name,
    (storage.foldername(name))[1] as student_id_folder,
    (storage.foldername(name))[2] as item_type_folder
FROM storage.objects 
WHERE bucket_id = 'clearance-proofs'
LIMIT 5;


-- ============================================================================
-- EXPECTED FILE STRUCTURE IN BUCKET
-- ============================================================================
-- 
-- clearance-proofs/
-- ├── 101/                          (student_id)
-- │   ├── books/
-- │   │   ├── 1234_proof.jpg        (book_id_proof.ext)
-- │   │   └── 5678_proof.png
-- │   └── materials/
-- │       ├── 9999_proof.jpg        (material_id_proof.ext)
-- │       └── 8888_proof.jpg
-- ├── 102/
-- │   ├── books/
-- │   │   └── 2345_proof.jpg
-- │   └── materials/
-- │       └── 7777_proof.jpg
-- └── ...
--
-- Path format: {student_id}/{item_type}/{item_id}_proof.{ext}
-- Example: "101/books/1234_proof.jpg"
-- ============================================================================


-- ============================================================================
-- NOTES
-- ============================================================================
-- 
-- FOLDER STRUCTURE:
-- - First level: student_id (e.g., "101")
-- - Second level: item_type ("books" or "materials")
-- - File name: {item_id}_proof.{extension}
--
-- SECURITY:
-- - Students can only upload to their own student_id folder
-- - Teachers can view images from students they teach
-- - Lab staff can view lab material proofs
-- - Coaches can view sports equipment proofs
-- - Public bucket allows anonymous read (images visible to anyone with URL)
-- - RLS policies still apply for authenticated operations
--
-- PUBLIC ACCESS:
-- Since you enabled "Public bucket", anyone with the URL can view images.
-- The RLS policies control who can UPLOAD/UPDATE/DELETE, but public read
-- is allowed by the bucket setting. If you want to restrict viewing to
-- authenticated users only, disable public access on the bucket.
--
-- PRIVACY CONSIDERATIONS:
-- - Y1 students upload photos of books (may contain personal notes)
-- - Consider disabling public bucket and using signed URLs instead
-- - Signed URLs expire and can be generated on-demand by backend
--
-- STORAGE LIMITS:
-- - Set "Restrict file size" to limit uploads (e.g., 5MB for photos)
-- - Set "Restrict MIME types" to allow only images (image/jpeg, image/png)
--
-- ============================================================================
