import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url:
    raise ValueError("SUPABASE_URL environment variable is not set")
if not key:
    raise ValueError("SUPABASE_KEY environment variable is not set")

supabase = create_client(url, key)

# ===============================
# STUDENT DATA FUNCTIONS
# ===============================

def get_student_by_id(student_id):
    """Get student details by student_id"""
    try:
        result = supabase.table('students').select('*').eq('student_id', student_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting student: {e}")
        return None

def get_student_classes(student_id):
    """Get all classes for a student with subject and teacher details"""
    try:
        result = supabase.table('student_classes').select('''
            *,
            class_id (
                class_id,
                class_name,
                teacher_id,
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
    """Get all books assigned to a student"""
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
    """Get all materials assigned to a student"""
    try:
        result = supabase.table('materials').select('*').eq('student_id', student_id).execute()
        return result.data
    except Exception as e:
        print(f"Error getting student materials: {e}")
        return []

def get_student_financial_overview(student_id):
    """Get financial overview for a student"""
    try:
        result = supabase.table('student_financial_overview').select('*').eq('student_id', student_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting financial overview: {e}")
        return None

def get_student_room(student_id):
    """Get room assignment for a student"""
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
                last_name
            )
        ''').eq('subject_id', subject_id).execute()
        return result.data
    except Exception as e:
        print(f"Error getting books by subject: {e}")
        return []

# ===============================
# FINANCE DATA FUNCTIONS
# ===============================

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
    """Calculate clearance percentage for a specific subject"""
    try:
        # Get books for this subject
        books = get_student_books(student_id)
        subject_books = [book for book in books if book.get('subject_id', {}).get('subject_id') == subject_id]
        
        # Get materials for this subject
        materials = get_student_materials(student_id)
        subject_materials = [material for material in materials if material.get('subject_id') == subject_id]
        
        total_items = len(subject_books) + len(subject_materials)
        if total_items == 0:
            return 100  # If no items, consider it cleared
        
        # Count returned/approved items
        returned_books = sum(1 for book in subject_books if book.get('returned', False))
        returned_materials = sum(1 for material in subject_materials if material.get('returned', False))
        
        returned_items = returned_books + returned_materials
        percentage = (returned_items / total_items) * 100
        
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
    """Calculate overall clearance percentage as average of all subject percentages"""
    try:
        # Get all student's enrolled classes
        student_classes = get_student_classes(student_id)
        
        if not student_classes:
            return 0
        
        total_percentage = 0
        subject_count = 0
        
        for enrollment in student_classes:
            subject_id = enrollment.get('class_id', {}).get('subject_id', {}).get('subject_id')
            if subject_id:
                subject_percentage = calculate_subject_clearance_percentage(student_id, subject_id)
                total_percentage += subject_percentage
                subject_count += 1
        
        if subject_count == 0:
            return 0
            
        overall_percentage = total_percentage / subject_count
        return round(overall_percentage)
        
    except Exception as e:
        print(f"Error calculating overall clearance percentage: {e}")
        return 0

def calculate_overall_clearance_status(student_id):
    """Calculate overall clearance status based on all subjects"""
    try:
        # Get all student's enrolled classes
        student_classes = get_student_classes(student_id)
        
        if not student_classes:
            return 'not-started'
        
        statuses = []
        for enrollment in student_classes:
            subject_id = enrollment.get('class_id', {}).get('subject_id', {}).get('subject_id')
            if subject_id:
                status = calculate_subject_clearance_status(student_id, subject_id)
                statuses.append(status)
        
        if not statuses:
            return 'not-started'
        
        # Determine overall status
        if all(status == 'approved' for status in statuses):
            return 'approved'
        elif any(status == 'pending' for status in statuses):
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

