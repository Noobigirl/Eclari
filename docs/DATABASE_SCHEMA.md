# Eclari Database Schema Documentation

> **Last Updated:** November 6, 2025  
> **Version:** 2.0 - Year Group Differentiated Clearance System

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Core Entities](#core-entities)
3. [Clearance System](#clearance-system)
4. [Block Scheduling](#block-scheduling)
5. [Approval Workflow](#approval-workflow)
6. [Storage & RLS](#storage--rls)
7. [Database Views](#database-views)
8. [Relationships Diagram](#relationships-diagram)

---

## Overview

The Eclari database manages a school clearance system with **year-group differentiated workflows**:

- **Y1 Students (Year 1):** Submit photo proof of books → Teachers approve digitally
- **Y2 Students (Year 2):** Physically return books → Teachers mark as returned
- **All Students:** Lab equipment and sports materials always require physical return

### Key Features
- 🎯 Role-based access (Students, Teachers, Lab Staff, Coaches, Finance, Hall)
- 📸 Image proof upload for Y1 students via Supabase Storage
- 🔒 Row-Level Security (RLS) on all tables
- ⏰ Block scheduling with color-coded time slots
- ✅ Multi-stage approval workflow with rejection reasons

---

## Core Entities

### 1. **students**
Stores student information and authentication.

| Column | Type | Description |
|--------|------|-------------|
| `student_id` | SERIAL | Primary key |
| `auth_uid` | TEXT | Supabase auth user ID (unique) |
| `first_name` | TEXT | Student first name |
| `last_name` | TEXT | Student last name |
| `email` | TEXT | Student email (unique) |
| `profile_image_url` | TEXT | Profile picture URL |
| `created_at` | TIMESTAMPTZ | Account creation timestamp |

**RLS Policies:**
- Students can view/update their own record only
- Teachers can view students in their classes
- Service role has full access

---

### 2. **teachers**
Stores teacher information and subject assignments.

| Column | Type | Description |
|--------|------|-------------|
| `teacher_id` | SERIAL | Primary key |
| `auth_uid` | TEXT | Supabase auth user ID (unique) |
| `first_name` | TEXT | Teacher first name |
| `last_name` | TEXT | Teacher last name |
| `email` | TEXT | Teacher email (unique) |
| `profile_image_url` | TEXT | Profile picture URL |
| `created_at` | TIMESTAMPTZ | Account creation timestamp |

**RLS Policies:**
- Teachers can view/update their own record
- Service role has full access

---

### 3. **subjects**
Defines available subjects in the school.

| Column | Type | Description |
|--------|------|-------------|
| `subject_id` | TEXT | Primary key (e.g., 'MATH', 'ENG', 'SCI', 'PE') |
| `subject_name` | TEXT | Display name (e.g., 'Mathematics', 'English') |
| `icon` | TEXT | Emoji icon for UI (e.g., '📐', '📖', '🔬', '⚽') |
| `color` | TEXT | Hex color for UI (e.g., '#3B82F6') |

**Special Subjects:**
- `SCI` - Science (used for lab equipment)
- `PE` - Physical Education (used for sports equipment)

---

### 4. **classes**
Represents a teaching group with year group and block schedule.

| Column | Type | Description |
|--------|------|-------------|
| `class_id` | SERIAL | Primary key |
| `class_name` | TEXT | Class identifier (e.g., 'Y1-Math-A', 'Y2-Physics-B') |
| `teacher_id` | INTEGER | FK → `teachers.teacher_id` |
| `subject_id` | TEXT | FK → `subjects.subject_id` |
| `year_group` | INTEGER | **NEW** Student year (1 or 2) |
| `color_block` | TEXT | **NEW** Time slot color (see Block Scheduling) |
| `created_at` | TIMESTAMPTZ | Class creation timestamp |

**Year Group Logic:**
- `year_group = 1` → Y1 students → Photo proof accepted
- `year_group = 2` → Y2 students → Physical return required

**Block Schedule Logic:**
- `color_block` identifies the TIME SLOT (not subject)
- All students have the same color block at the same time
- Different subjects can occur in the same time slot

**Indexes:**
- `idx_classes_year_group` on `year_group`
- `idx_classes_color_block` on `color_block`

---

### 5. **student_classes**
Junction table for many-to-many student-class relationships.

| Column | Type | Description |
|--------|------|-------------|
| `enrollment_id` | SERIAL | Primary key |
| `student_id` | INTEGER | FK → `students.student_id` |
| `class_id` | INTEGER | FK → `classes.class_id` |
| `enrolled_at` | TIMESTAMPTZ | Enrollment date |

**Constraints:**
- Unique constraint on `(student_id, class_id)`

---

## Clearance System

### 6. **books**
Tracks textbook assignments and clearance status.

| Column | Type | Description |
|--------|------|-------------|
| `book_id` | SERIAL | Primary key |
| `book_name` | TEXT | Book title |
| `subject_id` | TEXT | FK → `subjects.subject_id` |
| `student_id` | INTEGER | FK → `students.student_id` |
| `returned` | BOOLEAN | Physical return status (Y2 workflow) |
| `image_proof_url` | TEXT | **NEW** URL to proof image in storage |
| `approval_status` | TEXT | **NEW** 'pending', 'approved', 'rejected' |
| `approved_by` | TEXT | **NEW** teacher_id who approved (stored as TEXT) |
| `approved_at` | TIMESTAMPTZ | **NEW** Approval timestamp |
| `rejection_reason` | TEXT | **NEW** Reason if rejected |
| `submitted_at` | TIMESTAMPTZ | **NEW** When proof was submitted |
| `created_at` | TIMESTAMPTZ | Book assignment date |

**Workflow:**
1. **Y1 Student:** Uploads photo → `image_proof_url` set, `approval_status = 'pending'`
2. **Teacher:** Reviews photo → `approval_status = 'approved'` or `'rejected'`
3. **Y2 Student:** Physically returns → Teacher marks `returned = TRUE`

**RLS Policies:**
- Students can view their own books
- Students can update their own books (upload proof)
- Teachers can view/approve books for subjects they teach
- Service role has full access

**Indexes:**
- `idx_books_approval_status` on `approval_status`

---

### 7. **materials**
Tracks lab equipment and sports materials clearance.

| Column | Type | Description |
|--------|------|-------------|
| `material_id` | SERIAL | Primary key |
| `material_name` | TEXT | Equipment name (e.g., 'Lab Coat', 'Football') |
| `subject_id` | TEXT | FK → `subjects.subject_id` ('SCI' or 'PE') |
| `student_id` | INTEGER | FK → `students.student_id` |
| `returned` | BOOLEAN | Physical return status |
| `image_proof_url` | TEXT | **NEW** URL to proof image (rarely used) |
| `approval_status` | TEXT | **NEW** 'pending', 'approved', 'rejected' |
| `approved_by` | TEXT | **NEW** staff_id who approved (TEXT) |
| `approved_at` | TIMESTAMPTZ | **NEW** Approval timestamp |
| `rejection_reason` | TEXT | **NEW** Reason if rejected |
| `submitted_at` | TIMESTAMPTZ | **NEW** When proof was submitted |
| `created_at` | TIMESTAMPTZ | Material assignment date |

**Special Rules:**
- Lab equipment (`subject_id = 'SCI'`) **always** requires physical return
- Sports equipment (`subject_id = 'PE'`) **always** requires physical return
- Photo proof is NOT accepted for materials (regardless of year group)

**RLS Policies:**
- Students can view their own materials
- Lab staff can view/approve materials where `subject_id = 'SCI'`
- Coaches can view/approve materials where `subject_id = 'PE'`
- Service role has full access

**Indexes:**
- `idx_materials_approval_status` on `approval_status`

---

### 8. **lab_staff**
Lab technicians who manage science equipment.

| Column | Type | Description |
|--------|------|-------------|
| `staff_id` | SERIAL | Primary key |
| `auth_uid` | TEXT | Supabase auth user ID (unique) |
| `first_name` | TEXT | Staff first name |
| `last_name` | TEXT | Staff last name |
| `email` | TEXT | Staff email (unique) |
| `created_at` | TIMESTAMPTZ | Account creation timestamp |

**Permissions:**
- Can view/approve materials where `subject_id = 'SCI'`
- Can mark lab equipment as physically returned

---

### 9. **coaches**
PE staff who manage sports equipment.

| Column | Type | Description |
|--------|------|-------------|
| `coach_id` | SERIAL | Primary key |
| `auth_uid` | TEXT | Supabase auth user ID (unique) |
| `first_name` | TEXT | Coach first name |
| `last_name` | TEXT | Coach last name |
| `email` | TEXT | Coach email (unique) |
| `created_at` | TIMESTAMPTZ | Account creation timestamp |

**Permissions:**
- Can view/approve materials where `subject_id = 'PE'`
- Can mark sports equipment as physically returned

---

### 10. **finance_staff** & **hall_staff**
Additional staff roles for fee clearance and hall allocation.

| Column | Type | Description |
|--------|------|-------------|
| `staff_id` | SERIAL | Primary key |
| `auth_uid` | TEXT | Supabase auth user ID (unique) |
| `first_name` | TEXT | Staff first name |
| `last_name` | TEXT | Staff last name |
| `email` | TEXT | Staff email (unique) |
| `created_at` | TIMESTAMPTZ | Account creation timestamp |

---

## Block Scheduling

### Color Blocks = Time Slots

**Important:** Color blocks represent **TIME SLOTS**, not subjects!

| Color Block | Time Slot | Example |
|-------------|-----------|---------|
| `green` | 8:00 - 9:30 AM | Student A: Math, Student B: English |
| `yellow` | 9:30 - 11:00 AM | Student A: Science, Student B: Math |
| `blue` | 11:00 AM - 12:30 PM | Student A: History, Student B: Science |
| `red` | 1:30 - 3:00 PM | Student A: English, Student B: PE |
| `purple` | 3:00 - 4:30 PM | Student A: PE, Student B: History |
| `orange` | 4:30 - 6:00 PM | Student A: Art, Student B: Art |

### Example Schedule

**9:30 - 11:00 AM (Yellow Block):**
- **Student 101** has Math (class_id: 1, color_block: 'yellow')
- **Student 102** has Science (class_id: 5, color_block: 'yellow')
- **Student 103** has English (class_id: 9, color_block: 'yellow')

All three students have **different subjects** during the **same time slot**.

### Database Representation

```sql
-- Student 101's schedule
SELECT c.color_block, c.class_name, s.subject_name
FROM student_classes sc
JOIN classes c ON sc.class_id = c.class_id
JOIN subjects s ON c.subject_id = s.subject_id
WHERE sc.student_id = 101
ORDER BY c.color_block;

-- Result:
-- color_block | class_name | subject_name
-- green       | Y1-Math-A  | Mathematics
-- yellow      | Y1-Sci-B   | Science
-- blue        | Y1-Eng-C   | English
```

---

## Approval Workflow

### Y1 Student Workflow (Photo Proof)

```
┌─────────────┐
│   Student   │
│  Uploads    │
│   Photo     │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  image_proof_url    │
│  approval_status =  │
│     'pending'       │
│  submitted_at = NOW │
└──────┬──────────────┘
       │
       ▼
┌─────────────┐
│   Teacher   │
│   Reviews   │
└──────┬──────┘
       │
   ┌───┴───┐
   ▼       ▼
┌────┐   ┌────────┐
│ ✅ │   │   ❌   │
│ OK │   │ Reject │
└─┬──┘   └───┬────┘
  │          │
  ▼          ▼
┌──────┐  ┌─────────────────┐
│status│  │ status='rejected'│
│ =    │  │ rejection_reason │
│'appr'│  │ approved_by      │
│oved' │  │ approved_at      │
└──────┘  └─────────────────┘
```

### Y2 Student Workflow (Physical Return)

```
┌─────────────┐
│   Student   │
│ Physically  │
│  Returns    │
│    Book     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Teacher   │
│    Marks    │
│  Returned   │
└──────┬──────┘
       │
       ▼
┌──────────────┐
│ returned =   │
│     TRUE     │
│ (approval_   │
│  status not  │
│    used)     │
└──────────────┘
```

### Lab/Sports Equipment Workflow (All Students)

```
┌─────────────┐
│   Student   │
│ Physically  │
│  Returns    │
│  Equipment  │
└──────┬──────┘
       │
       ▼
┌──────────────┐
│  Lab Staff   │
│     or       │
│    Coach     │
│    Marks     │
│  Returned    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ returned =   │
│     TRUE     │
└──────────────┘
```

---

## Storage & RLS

### Supabase Storage Bucket: `clearance-proofs`

**Configuration:**
- Bucket Name: `clearance-proofs`
- Public Access: Enabled (images readable via URL)
- File Size Limit: 5 MB (recommended)
- Allowed MIME Types: `image/jpeg`, `image/png`, `image/heic`

### File Structure

```
clearance-proofs/
├── 101/                          (student_id)
│   ├── books/
│   │   ├── 1234_proof.jpg        (book_id_proof.ext)
│   │   └── 5678_proof.png
│   └── materials/
│       ├── 9999_proof.jpg        (material_id_proof.ext)
│       └── 8888_proof.jpg
├── 102/
│   ├── books/
│   │   └── 2345_proof.jpg
│   └── materials/
│       └── 7777_proof.jpg
└── ...
```

**Path Format:** `{student_id}/{item_type}/{item_id}_proof.{ext}`  
**Example:** `101/books/1234_proof.jpg`

### Storage RLS Policies

| Policy | Role | Action | Condition |
|--------|------|--------|-----------|
| Students upload | authenticated | INSERT | Own student_id folder only |
| Students view | authenticated | SELECT | Own images only |
| Teachers view | authenticated | SELECT | Images from students they teach |
| Lab staff view | authenticated | SELECT | Lab material images (SCI) |
| Coaches view | authenticated | SELECT | Sports material images (PE) |
| Service role | service_role | ALL | Full access |

---

## Database Views

### `teacher_pending_approvals`
Shows pending book approvals for teachers (filtered by subjects they teach).

```sql
CREATE VIEW teacher_pending_approvals AS
SELECT 
    b.book_id,
    b.book_name,
    b.subject_id,
    b.student_id,
    s.first_name || ' ' || s.last_name as student_name,
    b.image_proof_url,
    b.submitted_at,
    c.year_group,
    c.teacher_id
FROM books b
JOIN students s ON b.student_id = s.student_id
JOIN student_classes sc ON s.student_id = sc.student_id
JOIN classes c ON sc.class_id = c.class_id
WHERE b.approval_status = 'pending'
  AND c.subject_id = b.subject_id
  AND c.year_group = 1;  -- Only Y1 students
```

**Usage:**
```sql
-- Teacher sees only their pending approvals
SELECT * FROM teacher_pending_approvals
WHERE teacher_id = <current_teacher_id>;
```

---

### `staff_pending_material_approvals`
Shows pending material approvals for lab staff and coaches.

```sql
CREATE VIEW staff_pending_material_approvals AS
SELECT 
    m.material_id,
    m.material_name,
    m.subject_id,
    m.student_id,
    s.first_name || ' ' || s.last_name as student_name,
    m.image_proof_url,
    m.submitted_at,
    m.returned
FROM materials m
JOIN students s ON m.student_id = s.student_id
WHERE m.approval_status = 'pending'
  OR m.returned = FALSE;
```

**Usage:**
```sql
-- Lab staff sees only SCI materials
SELECT * FROM staff_pending_material_approvals
WHERE subject_id = 'SCI';

-- Coaches see only PE materials
SELECT * FROM staff_pending_material_approvals
WHERE subject_id = 'PE';
```

---

## Relationships Diagram

```
┌──────────────┐
│   students   │
│──────────────│
│ student_id   │◄───┐
│ auth_uid     │    │
│ first_name   │    │
│ last_name    │    │
└──────────────┘    │
                    │
                    │ FK
                    │
┌──────────────┐    │         ┌──────────────┐
│    books     │    │         │  materials   │
│──────────────│    │         │──────────────│
│ book_id      │    │         │ material_id  │
│ student_id   │────┘         │ student_id   │────┐
│ subject_id   │────┐         │ subject_id   │────┤
│ returned     │    │         │ returned     │    │
│ approval_*   │    │         │ approval_*   │    │
└──────────────┘    │         └──────────────┘    │
                    │                              │
                    │ FK                           │ FK
                    │                              │
                    ▼                              ▼
              ┌──────────────┐             ┌──────────────┐
              │   subjects   │             │   subjects   │
              │──────────────│             │──────────────│
              │ subject_id   │             │ subject_id   │
              │ subject_name │             └──────────────┘
              │ icon, color  │
              └──────────────┘
                    ▲
                    │ FK
                    │
              ┌──────────────┐
              │   classes    │
              │──────────────│
              │ class_id     │◄────┐
              │ teacher_id   │────┐│
              │ subject_id   │    ││
              │ year_group   │    ││ FK
              │ color_block  │    ││
              └──────────────┘    ││
                    ▲             ││
                    │ FK          ││
                    │             ││
         ┌──────────────────┐    ││
         │ student_classes  │    ││
         │──────────────────│    ││
         │ enrollment_id    │    ││
         │ student_id       │────┘│
         │ class_id         │     │
         └──────────────────┘     │
                                  │
                                  ▼
                          ┌──────────────┐
                          │   teachers   │
                          │──────────────│
                          │ teacher_id   │
                          │ auth_uid     │
                          │ first_name   │
                          │ last_name    │
                          └──────────────┘

┌──────────────┐        ┌──────────────┐
│  lab_staff   │        │   coaches    │
│──────────────│        │──────────────│
│ staff_id     │        │ coach_id     │
│ auth_uid     │        │ auth_uid     │
└──────────────┘        └──────────────┘
      │                        │
      └────────────┬───────────┘
                   │
                   │ Approve materials
                   ▼
           ┌──────────────┐
           │  materials   │
           │  (SCI/PE)    │
           └──────────────┘
```

---

## Key Business Rules

### 1. **Year Group Determines Workflow**
```sql
-- Check student's year group
SELECT c.year_group 
FROM student_classes sc
JOIN classes c ON sc.class_id = c.class_id
WHERE sc.student_id = ?;

-- If year_group = 1: Allow photo proof
-- If year_group = 2: Require physical return
```

### 2. **Materials Always Require Physical Return**
```sql
-- Materials ignore year_group
UPDATE materials 
SET returned = TRUE 
WHERE material_id = ?;
-- No approval_status check needed
```

### 3. **Teachers Can Only Approve Their Subjects**
```sql
-- Teacher approval check
SELECT COUNT(*) 
FROM classes c
JOIN teachers t ON c.teacher_id = t.teacher_id
WHERE t.teacher_id = ? 
  AND c.subject_id = ?;
-- Must be > 0 to approve
```

### 4. **Color Blocks Are Time Slots**
```sql
-- Get student's schedule for a specific time slot
SELECT c.class_name, s.subject_name
FROM student_classes sc
JOIN classes c ON sc.class_id = c.class_id
JOIN subjects s ON c.subject_id = s.subject_id
WHERE sc.student_id = ? 
  AND c.color_block = 'yellow';  -- 9:30-11:00 AM
```

---

## Migration Summary

### Changes from v1.0 to v2.0

**New Columns Added:**
- `classes`: `year_group`, `color_block`
- `books`: `image_proof_url`, `approval_status`, `approved_by`, `approved_at`, `rejection_reason`, `submitted_at`
- `materials`: `image_proof_url`, `approval_status`, `approved_by`, `approved_at`, `rejection_reason`, `submitted_at`

**New Indexes:**
- `idx_classes_year_group`
- `idx_classes_color_block`
- `idx_books_approval_status`
- `idx_materials_approval_status`

**New Views:**
- `teacher_pending_approvals`
- `staff_pending_material_approvals`

**New Storage Bucket:**
- `clearance-proofs` with RLS policies

**Migration Files:**
- `database_migration_year_groups_SAFE.sql` - Safe migration with rollback support
- `rls_policies_books.sql` - RLS for books table
- `rls_policies_materials.sql` - RLS for materials table
- `rls_policies_storage.sql` - RLS for storage bucket

---

## Quick Reference

### Check Clearance Status

```sql
-- Student's overall clearance percentage
SELECT 
    student_id,
    COUNT(*) as total_items,
    COUNT(CASE 
        WHEN c.year_group = 1 AND approval_status = 'approved' THEN 1
        WHEN c.year_group = 2 AND returned = TRUE THEN 1
    END) as cleared_items,
    ROUND(
        100.0 * COUNT(CASE 
            WHEN c.year_group = 1 AND approval_status = 'approved' THEN 1
            WHEN c.year_group = 2 AND returned = TRUE THEN 1
        END) / COUNT(*),
        2
    ) as clearance_percentage
FROM books b
JOIN student_classes sc ON b.student_id = sc.student_id
JOIN classes c ON sc.class_id = c.class_id AND c.subject_id = b.subject_id
WHERE b.student_id = ?
GROUP BY student_id;
```

### Pending Approvals Count

```sql
-- Count pending approvals for a teacher
SELECT COUNT(*) 
FROM teacher_pending_approvals
WHERE teacher_id = ?;

-- Count pending returns for lab staff
SELECT COUNT(*) 
FROM staff_pending_material_approvals
WHERE subject_id = 'SCI' AND returned = FALSE;
```

---

## Support

For questions or issues with the database schema, refer to:
- Backend implementation: `supabase_client.py`
- Frontend integration: `app.py`
- API documentation: (to be created)

---

**End of Documentation**
