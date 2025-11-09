"""
Eclari Supabase Client - Database Access Layer

This module provides all database access functions for the Eclari student clearance system.
It handles connections to Supabase and provides clean, typed interfaces for all data operations.

The functions are organized by entity type (students, teachers, hall, finance, etc.) 
and provide comprehensive error handling and data validation.

Author: Built with care for ALA students
Date: 2025
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables from .env file
load_dotenv()

# Get Supabase configuration from environment
url = os.getenv("SUPABASE_URL")
service_key = os.getenv("SUPABASE_KEY")  # Service role key for backend operations
anon_key = os.getenv("SUPABASE_ANON_KEY")  # Anonymous key for frontend/client operations

# Validate that required environment variables are set
if not url:
    raise ValueError("SUPABASE_URL environment variable is not set")
if not service_key:
    raise ValueError("SUPABASE_KEY environment variable is not set")
if not anon_key:
    raise ValueError("SUPABASE_ANON_KEY environment variable is not set")

# Create the Supabase client instance
# Use service key for server-side operations (database access)
supabase = create_client(url, service_key)

# Export these for use in templates and frontend
# IMPORTANT: Only export the anonymous key to the frontend, never the service key
supabase_url = url
supabase_anon_key = anon_key  # This is safe to use in browser

# ===== STUDENT DATA FUNCTIONS =====
# These functions handle all student-related data access

def get_student_by_id(student_id):
    """
    Get complete student profile information by student ID.
    
    Args:
        student_id (str): The unique student identifier
        
    Returns:
        dict: Student data including personal info, or None if not found
    """
    try:
        result = supabase.table('students').select('*').eq('student_id', student_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting student: {e}")
        return None

def get_student_classes(student_id):
    """
    Get all classes a student is enrolled in with complete details.
    
    This includes subject information and teacher details for each class.
    Essential for showing students their clearance status per subject.
    
    Args:
        student_id (str): The student's unique identifier
        
    Returns:
        list: List of enrollment records with nested class/subject/teacher/color_block data
    """
    try:
        result = supabase.table('student_classes').select('''
            *,
            class_id (
                class_id,
                class_name,
                teacher_id,
                color_block,
                subject_id (
                    subject_id,
                    subject_name
                )
            )
        ''').eq('student_id', student_id).execute()
        return result.data
    except Exception as e:
        print(f"Error getting student classes: {e}")
        return []

def get_student_books(student_id):
    """
    Get all books currently assigned to a student.
    
    This is crucial for clearance - students must return all books
    before they can be cleared. Includes subject information to 
    help students identify which books belong to which classes.
    
    Args:
        student_id (str): The student's unique identifier
        
    Returns:
        list: List of book records with subject details
    """
    try:
        result = supabase.table('books').select('''
            *,
            subject_id (
                subject_id,
                subject_name
            )
        ''').eq('student_id', student_id).execute()
        return result.data
    except Exception as e:
        print(f"Error getting student books: {e}")
        return []

def get_student_materials(student_id):
    """
    Get all lab/classroom materials currently assigned to a student.
    
    Students need to return lab equipment, sports gear, and other
    materials before clearance. This tracks what they still have.
    
    Args:
        student_id (str): The student's unique identifier
        
    Returns:
        list: List of material records assigned to the student
    """
    try:
        result = supabase.table('materials').select('*').eq('student_id', student_id).execute()
        return result.data
    except Exception as e:
        print(f"Error getting student materials: {e}")
        return []

def get_student_financial_overview(student_id):
    """
    Get financial status summary for a student.
    
    Shows outstanding fees, payment status, and financial clearance status.
    Critical for determining if student can be cleared financially.
    
    Args:
        student_id (str): The student's unique identifier
        
    Returns:
        dict: Financial overview data, or None if not found
    """
    try:
        result = supabase.table('student_financial_overview').select('*').eq('student_id', student_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting financial overview: {e}")
        return None

def get_student_room(student_id):
    """
    Get room assignment and hall information for a student.
    
    Students need hall clearance from their residential hall before
    final clearance. This shows which hall/room they're assigned to.
    
    Args:
        student_id (str): The student's unique identifier
        
    Returns:
        dict: Room assignment data, or None if not found
    """
    try:
        result = supabase.table('rooms').select('''
            *,
            hall_id (
                hall_id,
                first_name,
                last_name,
                hall_name
            )
        ''').eq('student_id', student_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting student room: {e}")
        return None

# ===============================
# TEACHER DATA FUNCTIONS
# ===============================

def get_teacher_by_id(teacher_id):
    """Get teacher details by teacher_id"""
    try:
        result = supabase.table('teachers').select('*').eq('teacher_id', teacher_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting teacher: {e}")
        return None

def get_teacher_classes(teacher_id):
    """Get all classes taught by a teacher"""
    try:
        result = supabase.table('classes').select('''
            *,
            subject_id (
                subject_id,
                subject_name
            )
        ''').eq('teacher_id', teacher_id).execute()
        return result.data
    except Exception as e:
        print(f"Error getting teacher classes: {e}")
        return []

def get_students_in_class(class_id):
    """Get all students enrolled in a specific class"""
    try:
        result = supabase.table('student_classes').select('''
            *,
            student_id (
                student_id,
                first_name,
                last_name,
                year_group
            )
        ''').eq('class_id', class_id).execute()
        return result.data
    except Exception as e:
        print(f"Error getting students in class: {e}")
        return []

def get_books_by_subject(subject_id):
    """Get all books for a specific subject"""
    try:
        result = supabase.table('books').select('''
            *,
            student_id (
                student_id,
                first_name,
                last_name,
                year_group
            )
        ''').eq('subject_id', subject_id).execute()
        return result.data
    except Exception as e:
        print(f"Error getting books by subject: {e}")
        return []

# ===============================
# FINANCE DATA FUNCTIONS
# ===============================

def get_finance_staff_by_id(finance_id):
    """Get finance staff details by finance_id"""
    try:
        result = supabase.table('finance_staff').select('*').eq('finance_id', finance_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting finance staff: {e}")
        return None

def get_financial_overview():
    """Get financial overview statistics for finance dashboard"""
    try:
        # Get all financial records
        all_records = supabase.table('finance').select('*').execute()
        
        if not all_records.data:
            return {
                'total_tuition': 0,
                'total_paid': 0,
                'total_outstanding': 0,
                'paid_count': 0,
                'partial_count': 0,
                'outstanding_count': 0
            }
        
        total_tuition = sum(record['tuition_due'] for record in all_records.data)
        total_paid = sum(record['amount_paid'] for record in all_records.data)
        total_outstanding = sum(record['balance'] for record in all_records.data)
        
        paid_count = len([r for r in all_records.data if r['status'] == 'Paid'])
        partial_count = len([r for r in all_records.data if r['status'] == 'Partial'])
        outstanding_count = len([r for r in all_records.data if r['status'] == 'Outstanding'])
        
        return {
            'total_tuition': total_tuition,
            'total_paid': total_paid,
            'total_outstanding': total_outstanding,
            'paid_count': paid_count,
            'partial_count': partial_count,
            'outstanding_count': outstanding_count
        }
    except Exception as e:
        print(f"Error getting financial overview: {e}")
        return None

def get_all_financial_records():
    """Get all financial records with student details"""
    try:
        result = supabase.table('finance').select('''
            *,
            student_id (
                student_id,
                first_name,
                last_name
            )
        ''').execute()
        return result.data
    except Exception as e:
        print(f"Error getting financial records: {e}")
        return []

def get_financial_record(student_id):
    """Get financial record for a specific student"""
    try:
        result = supabase.table('finance').select('*').eq('student_id', student_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting financial record: {e}")
        return None

def update_financial_record(student_id, updates):
    """Update financial record for a student"""
    try:
        result = supabase.table('finance').update(updates).eq('student_id', student_id).execute()
        return result.data
    except Exception as e:
        print(f"Error updating financial record: {e}")
        return None

# ===============================
# HALL DATA FUNCTIONS
# ===============================

def get_hall_head_by_id(hall_id):
    """Get hall head details by hall_id"""
    try:
        result = supabase.table('hall_heads').select('*').eq('hall_id', hall_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting hall head: {e}")
        return None

def get_rooms_by_hall(hall_id):
    """Get all rooms managed by a hall head"""
    try:
        result = supabase.table('rooms').select('''
            *,
            student_id (
                student_id,
                first_name,
                last_name,
                year_group
            )
        ''').eq('hall_id', hall_id).execute()
        return result.data
    except Exception as e:
        print(f"Error getting rooms by hall: {e}")
        return []

def get_all_rooms():
    """Get all rooms with student and hall details"""
    try:
        result = supabase.table('rooms').select('''
            *,
            student_id (
                student_id,
                first_name,
                last_name,
                year_group
            ),
            hall_id (
                hall_id,
                first_name,
                last_name,
                hall_name
            )
        ''').execute()
        return result.data
    except Exception as e:
        print(f"Error getting all rooms: {e}")
        return []

# ===============================
# MATERIALS DATA FUNCTIONS
# ===============================

def get_materials_by_subject(subject_id):
    """Get all materials for a specific subject"""
    try:
        result = supabase.table('materials').select('''
            *,
            student_id (
                student_id,
                first_name,
                last_name
            )
        ''').eq('subject_id', subject_id).execute()
        return result.data
    except Exception as e:
        print(f"Error getting materials by subject: {e}")
        return []

def get_all_materials():
    """Get all materials with student details"""
    try:
        result = supabase.table('materials').select('''
            *,
            student_id (
                student_id,
                first_name,
                last_name
            )
        ''').execute()
        return result.data
    except Exception as e:
        print(f"Error getting all materials: {e}")
        return []

def update_material_status(material_id, returned):
    """Update material return status"""
    try:
        result = supabase.table('materials').update({'returned': returned}).eq('material_id', material_id).execute()
        return result.data
    except Exception as e:
        print(f"Error updating material status: {e}")
        return None

def update_book_status(book_id, returned):
    """Update book return status"""
    try:
        result = supabase.table('books').update({'returned': returned}).eq('book_id', book_id).execute()
        return result.data
    except Exception as e:
        print(f"Error updating book status: {e}")
        return None

# ===============================
# GENERAL DATA FUNCTIONS
# ===============================

def get_all_subjects():
    """Get all subjects"""
    try:
        result = supabase.table('subjects').select('*').execute()
        return result.data
    except Exception as e:
        print(f"Error getting subjects: {e}")
        return []

def get_all_students():
    """Get all students"""
    try:
        result = supabase.table('students').select('*').execute()
        return result.data
    except Exception as e:
        print(f"Error getting all students: {e}")
        return []

def get_all_teachers():
    """Get all teachers"""
    try:
        result = supabase.table('teachers').select('*').execute()
        return result.data
    except Exception as e:
        print(f"Error getting all teachers: {e}")
        return []

def search_students(search_term):
    """Search students by name or ID"""
    try:
        result = supabase.table('students').select('*').or_(
            f'first_name.ilike.%{search_term}%,last_name.ilike.%{search_term}%,student_id.ilike.%{search_term}%'
        ).execute()
        return result.data
    except Exception as e:
        print(f"Error searching students: {e}")
        return []

def calculate_subject_clearance_percentage(student_id, subject_id):
    """
    Calculate clearance percentage for a specific subject.
    
    NEW LOGIC (Year Group Aware):
    - Y1 Students: Cleared = approval_status == 'approved' OR returned == True (fallback for testing)
    - Y2 Students: Cleared = returned == True
    - Lab/Sports Materials: ALWAYS require physical return (returned == True)
    """
    try:
        # Get student to check year group
        student = get_student_by_id(student_id)
        if not student:
            return 0
        
        year_group = student.get('year_group', 2)  # Default to Y2 if not set
        
        # Get books for this subject
        books = get_student_books(student_id)
        subject_books = [book for book in books if book.get('subject_id', {}).get('subject_id') == subject_id]
        
        # Get materials for this subject
        materials = get_student_materials(student_id)
        subject_materials = [material for material in materials if material.get('subject_id') == subject_id]
        
        total_items = len(subject_books) + len(subject_materials)
        if total_items == 0:
            return 100  # If no items, consider it cleared
        
        # Count cleared items based on year group
        cleared_count = 0
        
        # Books: Y1 uses approval_status OR returned (for testing), Y2 uses returned
        for book in subject_books:
            if year_group == 1:
                # Y1: Check approval_status OR returned (fallback for direct DB testing)
                if book.get('approval_status') == 'approved' or book.get('returned', False):
                    cleared_count += 1
            else:
                # Y2: Check returned status
                if book.get('returned', False):
                    cleared_count += 1
        
        # Materials: ALWAYS require physical return (both Y1 and Y2)
        for material in subject_materials:
            if material.get('returned', False):
                cleared_count += 1
        
        percentage = (cleared_count / total_items) * 100
        return round(percentage)
        
    except Exception as e:
        print(f"Error calculating subject clearance percentage: {e}")
        return 0

def calculate_subject_clearance_status(student_id, subject_id):
    """Calculate clearance status for a specific subject"""
    try:
        # Get the percentage first
        percentage = calculate_subject_clearance_percentage(student_id, subject_id)
        
        # Simple logic based on percentage
        if percentage == 100:
            return 'approved'
        elif percentage > 0:
            return 'pending'  # Some items returned, others pending
        else:
            return 'not-started'  # No items returned
            
    except Exception as e:
        print(f"Error calculating subject clearance status: {e}")
        return 'not-started'

def calculate_overall_clearance_percentage(student_id):
    """
    Calculate overall clearance percentage including:
    - All books (from all subjects)
    - ALL materials (including non-subject materials like sports gear, art kits)
    - Financial clearance
    
    Note: Hall clearance is managed separately by hall heads
    """
    try:
        student = get_student_by_id(student_id)
        if not student:
            print(f"[DEBUG] Student not found: {student_id}")
            return 0
        
        year_group = student.get('year_group', 2)
        print(f"[DEBUG] Student {student_id}, Year Group: {year_group}")
        
        # Get all books
        books = get_student_books(student_id)
        print(f"[DEBUG] Total books: {len(books)}")
        
        # Get ALL materials (not filtered by subject)
        materials = get_student_materials(student_id)
        print(f"[DEBUG] Total materials: {len(materials)}")
        
        # Calculate total items and cleared items
        total_items = len(books) + len(materials)
        
        # Add financial check (1 item)
        financial = get_student_financial_overview(student_id)
        if financial:
            total_items += 1
            print(f"[DEBUG] Financial overview exists, tuition_due: {financial.get('tuition_due', 0)}")
        
        print(f"[DEBUG] Total items to clear: {total_items}")
        
        if total_items == 0:
            print("[DEBUG] No items to clear, returning 100%")
            return 100  # No items to clear
        
        cleared_count = 0
        
        # Count cleared books
        for book in books:
            book_returned = book.get('returned', False)
            book_approved = book.get('approval_status') == 'approved'
            if year_group == 1:
                if book_approved or book_returned:
                    cleared_count += 1
                    print(f"[DEBUG] Book {book.get('book_id')} cleared (approved={book_approved}, returned={book_returned})")
                else:
                    print(f"[DEBUG] Book {book.get('book_id')} NOT cleared (approved={book_approved}, returned={book_returned})")
            else:
                if book_returned:
                    cleared_count += 1
                    print(f"[DEBUG] Book {book.get('book_id')} cleared (returned={book_returned})")
                else:
                    print(f"[DEBUG] Book {book.get('book_id')} NOT cleared (returned={book_returned})")
        
        # Count cleared materials (ALL materials, regardless of subject)
        for material in materials:
            material_returned = material.get('returned', False)
            if material_returned:
                cleared_count += 1
                print(f"[DEBUG] Material {material.get('material_name')} cleared")
            else:
                print(f"[DEBUG] Material {material.get('material_name')} NOT cleared")
        
        # Check financial clearance
        if financial:
            if financial.get('tuition_due', 0) == 0:
                cleared_count += 1
                print(f"[DEBUG] Financial cleared")
            else:
                print(f"[DEBUG] Financial NOT cleared (due: ${financial.get('tuition_due', 0)})")
        
        percentage = (cleared_count / total_items) * 100
        print(f"[DEBUG] Final: {cleared_count}/{total_items} = {percentage}%")
        return round(percentage)
        
    except Exception as e:
        print(f"Error calculating overall clearance percentage: {e}")
        import traceback
        traceback.print_exc()
        return 0

def calculate_overall_clearance_status(student_id):
    """
    Calculate overall clearance status based on percentage.
    Simpler approach: just check if percentage is 100%
    """
    try:
        percentage = calculate_overall_clearance_percentage(student_id)
        
        if percentage == 100:
            return 'approved'
        elif percentage > 0:
            return 'pending'
        else:
            return 'not-started'
            
    except Exception as e:
        print(f"Error calculating overall clearance status: {e}")
        return 'not-started'

def get_students_by_hall_with_clearance(hall_id):
    """Get students in a hall with their room assignments and hall-specific status"""
    try:
        # Get all rooms in the hall with student assignments
        result = supabase.table('rooms').select('''
            *,
            student_id (
                student_id,
                first_name,
                last_name,
                year_group
            )
        ''').eq('hall_id', hall_id).execute()
        
        students_data = []
        for room in result.data:
            if room['student_id'] and isinstance(room['student_id'], dict):  # Only include rooms with assigned students
                student = room['student_id']
                    
                students_data.append({
                    'student_id': student['student_id'],
                    'first_name': student['first_name'],
                    'last_name': student['last_name'],
                    'year_group': student.get('year_group', 'N/A'),
                    'room_number': room.get('room_id', 'N/A'),
                    'room_status': room.get('room_status', 'pending_inspection'),
                    'hall_clearance_status': room.get('hall_clearance_status', 'pending'),
                    'hall_name': room.get('hall_name', 'Unknown Hall')
                })
        
        return students_data
    except Exception as e:
        print(f"Error getting students by hall: {e}")
        # If there are database issues, return empty list instead of dummy data
        return []


# ===============================
# YEAR GROUP WORKFLOW FUNCTIONS
# ===============================
# These functions support the new Y1/Y2 differentiated clearance workflow

def get_pending_approvals_for_teacher(teacher_id):
    """
    Get all pending photo proof submissions for a teacher's subjects.
    Used by teacher dashboard to show Y1 student submissions awaiting approval.
    
    Args:
        teacher_id (str): The teacher's unique identifier
        
    Returns:
        dict: { 'books': [...], 'materials': [...] } with pending items
    """
    try:
        # Get teacher's classes to find their subjects
        teacher_classes = get_teacher_classes(teacher_id)
        subject_ids = [c['subject_id']['subject_id'] for c in teacher_classes if c.get('subject_id')]
        
        if not subject_ids:
            return {'books': [], 'materials': []}
        
        # Get books pending approval for these subjects
        books_result = supabase.table('books').select('''
            *,
            student_id (
                student_id,
                first_name,
                last_name,
                year_group
            ),
            subject_id (
                subject_id,
                subject_name
            )
        ''').in_('subject_id', subject_ids).eq('approval_status', 'pending').not_.is_('image_proof_url', 'null').execute()
        
        # For materials, teachers don't approve - lab staff and coaches do
        # So we return empty materials list for teachers
        
        return {
            'books': books_result.data if books_result.data else [],
            'materials': []
        }
        
    except Exception as e:
        print(f"Error getting pending approvals for teacher: {e}")
        return {'books': [], 'materials': []}


def get_pending_approvals_for_staff(staff_id, staff_role):
    """
    Get pending material approvals for lab staff or coaches.
    
    Args:
        staff_id (str): The staff member's ID (lab_staff_id or coach_id)
        staff_role (str): 'lab' or 'coach'
        
    Returns:
        list: Pending material submissions
    """
    try:
        subject_id = 'SCI' if staff_role == 'lab' else 'PE'
        
        result = supabase.table('materials').select('''
            *,
            student_id (
                student_id,
                first_name,
                last_name,
                year_group
            )
        ''').eq('subject_id', subject_id).eq('approval_status', 'pending').not_.is_('image_proof_url', 'null').execute()
        
        return result.data if result.data else []
        
    except Exception as e:
        print(f"Error getting pending material approvals: {e}")
        return []


def approve_book(book_id, teacher_id, action='approve', rejection_reason=None):
    """
    Approve or reject a Y1 student's book photo proof submission.
    
    When approved, sets both approval_status='approved' AND returned=true
    This ensures consistency between approval workflow and testing via DB edits.
    
    Args:
        book_id (str): The book ID
        teacher_id (str): The teacher approving/rejecting
        action (str): 'approve' or 'reject'
        rejection_reason (str, optional): Reason for rejection (required if action='reject')
        
    Returns:
        dict: Updated book record, or None on failure
    """
    try:
        from datetime import datetime
        
        update_data = {
            'approved_by': teacher_id,
            'approved_at': datetime.utcnow().isoformat()
        }
        
        if action == 'approve':
            update_data['approval_status'] = 'approved'
            update_data['returned'] = True  # Also mark as returned for consistency
            update_data['rejection_reason'] = None  # Clear any previous rejection
        elif action == 'reject':
            update_data['approval_status'] = 'rejected'
            update_data['returned'] = False  # Ensure not marked as returned
            if rejection_reason:
                update_data['rejection_reason'] = rejection_reason
        else:
            print(f"Invalid action: {action}")
            return None
        
        result = supabase.table('books').update(update_data).eq('book_id', book_id).execute()
        return result.data[0] if result.data else None
        
    except Exception as e:
        print(f"Error approving/rejecting book: {e}")
        return None


def approve_material(material_id, staff_id, action='approve', rejection_reason=None):
    """
    Approve or reject a Y1 student's material photo proof submission.
    
    When approved, sets both approval_status='approved' AND returned=true
    This ensures consistency between approval workflow and testing via DB edits.
    
    Args:
        material_id (str): The material ID
        staff_id (str): The staff member approving (lab_staff_id or coach_id)
        action (str): 'approve' or 'reject'
        rejection_reason (str, optional): Reason for rejection
        
    Returns:
        dict: Updated material record, or None on failure
    """
    try:
        from datetime import datetime
        
        update_data = {
            'approved_by': staff_id,
            'approved_at': datetime.utcnow().isoformat()
        }
        
        if action == 'approve':
            update_data['approval_status'] = 'approved'
            update_data['returned'] = True  # Also mark as returned for consistency
            update_data['rejection_reason'] = None
        elif action == 'reject':
            update_data['approval_status'] = 'rejected'
            update_data['returned'] = False  # Ensure not marked as returned
            if rejection_reason:
                update_data['rejection_reason'] = rejection_reason
        else:
            print(f"Invalid action: {action}")
            return None
        
        result = supabase.table('materials').update(update_data).eq('material_id', material_id).execute()
        return result.data[0] if result.data else None
        
    except Exception as e:
        print(f"Error approving/rejecting material: {e}")
        return None


def upload_proof_image(item_type, item_id, student_id, file_path):
    """
    Upload a proof image to Supabase Storage and update the record.
    
    This function handles the file upload to Supabase Storage and updates
    the corresponding database record with the image URL.
    
    Args:
        item_type (str): 'book' or 'material'
        item_id (str): The book_id or material_id
        student_id (str): The student's ID (for organizing storage)
        file_path (str): Path to the image file to upload
        
    Returns:
        dict: { 'success': bool, 'image_url': str } or error info
    """
    try:
        from datetime import datetime
        import os
        
        print(f"[DEBUG upload_proof_image] Starting upload - type: {item_type}, id: {item_id}, student: {student_id}")
        
        # Verify file exists
        if not os.path.exists(file_path):
            print(f"[ERROR] File not found: {file_path}")
            return {
                'success': False,
                'message': f'File not found: {file_path}'
            }
        
        # Generate unique filename
        timestamp = int(datetime.utcnow().timestamp())
        file_ext = os.path.splitext(file_path)[1]
        storage_path = f"{item_type}s/{student_id}/{item_id}_{timestamp}{file_ext}"
        
        print(f"[DEBUG] Storage path: {storage_path}")
        
        # Read file data
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        print(f"[DEBUG] File data read: {len(file_data)} bytes")
        
        # Determine content type based on file extension
        content_type = "image/jpeg"
        if file_ext.lower() in ['.png']:
            content_type = "image/png"
        elif file_ext.lower() in ['.heic']:
            content_type = "image/heic"
        
        print(f"[DEBUG] Content type: {content_type}")
        
        # Upload to Supabase Storage
        print(f"[DEBUG] Uploading to Supabase Storage bucket: clearance-proofs")
        try:
            result = supabase.storage.from_('clearance-proofs').upload(
                path=storage_path,
                file=file_data,
                file_options={"content-type": content_type, "upsert": "true"}
            )
            print(f"[DEBUG] Upload result: {result}")
        except Exception as upload_error:
            print(f"[ERROR] Supabase upload failed: {upload_error}")
            # Check if bucket exists
            try:
                buckets = supabase.storage.list_buckets()
                print(f"[DEBUG] Available buckets: {[b['name'] for b in buckets]}")
                if 'clearance-proofs' not in [b['name'] for b in buckets]:
                    return {
                        'success': False,
                        'message': 'Storage bucket "clearance-proofs" does not exist. Please contact administrator.'
                    }
            except Exception as bucket_check_error:
                print(f"[ERROR] Could not check buckets: {bucket_check_error}")
            
            return {
                'success': False,
                'message': f'Upload failed: {str(upload_error)}'
            }
        
        # Get public URL
        print(f"[DEBUG] Getting public URL...")
        public_url = supabase.storage.from_('clearance-proofs').get_public_url(storage_path)
        print(f"[DEBUG] Public URL: {public_url}")
        
        # Update database record
        table_name = 'books' if item_type == 'book' else 'materials'
        id_column = 'book_id' if item_type == 'book' else 'material_id'
        
        print(f"[DEBUG] Updating {table_name} table, column {id_column} = {item_id}")
        
        try:
            update_result = supabase.table(table_name).update({
                'image_proof_url': public_url,
                'submitted_at': datetime.utcnow().isoformat(),
                'approval_status': 'pending'
            }).eq(id_column, item_id).execute()
            
            print(f"[DEBUG] Database update result: {update_result.data}")
            
            if update_result.data:
                return {
                    'success': True,
                    'image_url': public_url,
                    'message': 'Proof image uploaded successfully'
                }
            else:
                print(f"[ERROR] No rows updated in database. Item {item_id} may not exist.")
                return {
                    'success': False,
                    'message': f'{item_type.capitalize()} ID "{item_id}" not found. Please check the ID and try again.'
                }
        except Exception as db_error:
            print(f"[ERROR] Database update failed: {db_error}")
            return {
                'success': False,
                'message': f'Database update failed: {str(db_error)}'
            }
        
    except Exception as e:
        print(f"[ERROR] Exception in upload_proof_image: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'message': f'Upload failed: {str(e)}'
        }


def get_class_by_id(class_id):
    """
    Get complete class information including year_group and color_block.
    
    Args:
        class_id (str): The class identifier
        
    Returns:
        dict: Class data with subject, teacher, year_group, color_block
    """
    try:
        result = supabase.table('classes').select('''
            *,
            subject_id (
                subject_id,
                subject_name
            ),
            teacher_id (
                teacher_id,
                first_name,
                last_name
            )
        ''').eq('class_id', class_id).execute()
        
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting class: {e}")
        return None


def get_y1_students_books(student_id):
    """
    Get books for Y1 student with approval workflow information.
    Includes image_proof_url, approval_status, rejection_reason.
    
    Args:
        student_id (str): The student's ID
        
    Returns:
        list: Books with approval workflow data
    """
    try:
        result = supabase.table('books').select('''
            *,
            subject_id (
                subject_id,
                subject_name
            )
        ''').eq('student_id', student_id).execute()
        
        return result.data if result.data else []
    except Exception as e:
        print(f"Error getting Y1 student books: {e}")
        return []


