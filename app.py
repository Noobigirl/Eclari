from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from supabase_client import supabase
from supabase_client import (
    get_student_by_id, get_student_classes, get_student_books, get_student_materials,
    get_student_financial_overview, get_student_room, get_teacher_by_id, get_teacher_classes,
    get_students_in_class, get_books_by_subject, get_all_financial_records, 
    get_financial_record, get_hall_head_by_id, get_rooms_by_hall, get_all_rooms,
    get_materials_by_subject, get_all_materials, get_all_subjects, get_all_students,
    get_all_teachers, search_students, calculate_subject_clearance_percentage,
    calculate_subject_clearance_status, calculate_overall_clearance_percentage,
    calculate_overall_clearance_status, get_students_by_hall_with_clearance
)
import os
import jwt
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-change-this')
    
    # Supabase config for frontend
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')
    
    def verify_supabase_token(f):
        """Decorator to verify Supabase JWT token and get user data"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get token from cookie
            token = request.cookies.get('supabase-token')
            
            if not token:
                flash('Please log in to access this page.', 'error')
                return redirect(url_for('login'))
            
            try:
                # Verify JWT token with Supabase
                response = supabase.auth.get_user(token)
                
                if response.user is None:
                    raise ValueError("Invalid token")
                
                auth_uid = response.user.id
                email = response.user.email
                
                # Determine user role and get user data from your tables
                user_data = get_user_data_by_auth_uid(auth_uid)
                
                if not user_data:
                    flash('User not found in system. Please contact administrator.', 'error')
                    return redirect(url_for('login'))
                
                # Store user info in session for route access
                session['user'] = user_data
                
                return f(*args, **kwargs)
                
            except Exception as e:
                print(f"Token verification error: {e}")
                flash('Your session has expired. Please log in again.', 'error')
                return redirect(url_for('login'))
        
        return decorated_function
    
    def get_user_data_by_auth_uid(auth_uid):
        """Get user data from student/teacher/staff tables by auth_uid"""
        try:
            # Check students table
            student = supabase.table('students').select('*').eq('auth_uid', auth_uid).execute()
            if student.data:
                user = student.data[0]
                return {
                    'id': user['student_id'],
                    'auth_uid': auth_uid,
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'role': 'student',
                    'year_group': user.get('year_group')
                }
            
            # Check teachers table
            teacher = supabase.table('teachers').select('*').eq('auth_uid', auth_uid).execute()
            if teacher.data:
                user = teacher.data[0]
                return {
                    'id': user['teacher_id'],
                    'auth_uid': auth_uid,
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'role': 'teacher'
                }
            
            # Check hall_heads table
            hall_head = supabase.table('hall_heads').select('*').eq('auth_uid', auth_uid).execute()
            if hall_head.data:
                user = hall_head.data[0]
                return {
                    'id': user['hall_id'],
                    'auth_uid': auth_uid,
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'role': 'hall',
                    'hall_name': user.get('hall_name')
                }
            
            # Add checks for other staff tables as needed
            # finance, coaches, etc.
            
            return None
            
        except Exception as e:
            print(f"Error getting user data: {e}")
            return None

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/login")
    def login():
        # Check if user is already logged in
        token = request.cookies.get('supabase-token')
        if token:
            try:
                response = supabase.auth.get_user(token)
                if response.user:
                    # User is already logged in, get their actual role from database
                    auth_uid = response.user.id
                    user_data = get_user_data_by_auth_uid(auth_uid)
                    
                    if user_data:
                        # Redirect to their proper dashboard
                        return redirect(url_for('dashboard', role=user_data['role']))
            except Exception as e:
                print(f"Login redirect error: {e}")
                # Clear invalid token
                response = redirect(url_for('login'))
                response.set_cookie('supabase-token', '', expires=0, path='/')
                response.set_cookie('user-info', '', expires=0, path='/')
                return response
        
        return render_template("login.html", 
                             supabase_url=supabase_url, 
                             supabase_anon_key=supabase_anon_key)

    @app.route("/dashboard/<role>")
    @verify_supabase_token
    def dashboard(role):
        """Role-based dashboard routing with real data integration"""
        user = session.get('user', {})
        user_role = user.get('role', 'student')
        
        # Ensure user can only access their designated dashboard
        if user_role != role and role != 'student':  # Allow fallback to student
            flash(f'Access denied. You are registered as a {user_role}.', 'error')
            return redirect(url_for('dashboard', role=user_role))
        
        # Prepare data based on role
        dashboard_data = {
            'user': user,
            'supabase_url': supabase_url,
            'supabase_anon_key': supabase_anon_key
        }
        
        if role == 'student':
            student_id = user.get('id')
            student_classes = get_student_classes(student_id)
            
            # Calculate subject-specific clearance data
            for enrollment in student_classes:
                subject_id = enrollment.get('class_id', {}).get('subject_id', {}).get('subject_id')
                if subject_id:
                    enrollment['clearance_percentage'] = calculate_subject_clearance_percentage(student_id, subject_id)
                    enrollment['clearance_status'] = calculate_subject_clearance_status(student_id, subject_id)
            
            dashboard_data.update({
                'student_classes': student_classes,
                'student_books': get_student_books(student_id),
                'student_materials': get_student_materials(student_id),
                'financial_overview': get_student_financial_overview(student_id),
                'room_assignment': get_student_room(student_id),
                'overall_clearance_percentage': calculate_overall_clearance_percentage(student_id),
                'overall_clearance_status': calculate_overall_clearance_status(student_id)
            })
        
        elif role == 'teacher':
            teacher_id = user.get('id')
            teacher_classes = get_teacher_classes(teacher_id)
            dashboard_data.update({
                'teacher_classes': teacher_classes,
                'all_subjects': get_all_subjects()
            })
            
            # Get students for each class
            for class_info in teacher_classes:
                class_info['students'] = get_students_in_class(class_info['class_id'])
                if class_info.get('subject_id'):
                    class_info['books'] = get_books_by_subject(class_info['subject_id']['subject_id'])
        
        elif role == 'finance':
            dashboard_data.update({
                'financial_records': get_all_financial_records(),
                'all_students': get_all_students()
            })
        
        elif role == 'hall':
            hall_id = user.get('id')
            hall_info = get_hall_head_by_id(hall_id)
            dashboard_data.update({
                'hall_rooms': get_rooms_by_hall(hall_id),
                'hall_info': hall_info,
                'hall_students': get_students_by_hall_with_clearance(hall_id),
                'hall_name': hall_info.get('hall_name') if hall_info else 'Unknown Hall'
            })
        
        elif role == 'lab':
            dashboard_data.update({
                'lab_materials': get_materials_by_subject('SCI'),  # Science materials
                'all_materials': get_all_materials()
            })
        
        elif role == 'coach':
            dashboard_data.update({
                'sports_materials': get_materials_by_subject('PE'),  # PE/Sports materials
                'all_students': get_all_students()
            })
        
        # Route to appropriate template based on role
        template_map = {
            'student': 'student.html',
            'teacher': 'teacher.html',
            'finance': 'finance.html',
            'hall': 'hall.html',
            'coach': 'coach.html',
            'lab': 'lab.html'
        }
        
        template = template_map.get(role, 'student.html')
        return render_template(template, **dashboard_data)

    @app.route("/logout")
    def logout():
        """Clear session and redirect to login"""
        session.clear()
        response = redirect(url_for('login'))
        # Clear the Supabase token cookies
        response.set_cookie('supabase-token', '', expires=0, path='/')
        response.set_cookie('user-info', '', expires=0, path='/')
        flash('You have been logged out successfully.', 'info')
        return response

    # Legacy routes - redirect to new dashboard routes
    @app.route("/student")
    @verify_supabase_token
    def student():
        return redirect(url_for('dashboard', role='student'))

    @app.route("/teacher")
    @verify_supabase_token
    def teacher():
        return redirect(url_for('dashboard', role='teacher'))

    @app.route("/finance")
    @verify_supabase_token
    def finance():
        return redirect(url_for('dashboard', role='finance'))

    @app.route("/hall")
    @verify_supabase_token
    def hall():
        return redirect(url_for('dashboard', role='hall'))

    @app.route("/coach")
    @verify_supabase_token
    def coach():
        return redirect(url_for('dashboard', role='coach'))

    @app.route("/lab")
    @verify_supabase_token
    def lab():
        return redirect(url_for('dashboard', role='lab'))

    @app.route("/subject")
    @app.route("/subject/<subject_id>")
    @verify_supabase_token
    def subject(subject_id=None):
        """Subject-specific clearance page"""
        user = session.get('user', {})
        student_id = user.get('id')
        
        if not subject_id:
            # If no subject specified, redirect to dashboard
            return redirect(url_for('dashboard', role=user.get('role', 'student')))
        
        # Get subject name from query parameter
        subject_name = request.args.get('name', subject_id)
        
        # Get student's data for this specific subject
        student_books_for_subject = []
        student_materials_for_subject = []
        
        # Get all student books and filter by subject
        all_books = get_student_books(student_id)
        student_books_for_subject = [book for book in all_books if book.get('subject_id', {}).get('subject_id') == subject_id]
        
        # Get all student materials and filter by subject
        all_materials = get_student_materials(student_id)
        student_materials_for_subject = [material for material in all_materials if material.get('subject_id') == subject_id]
        
        # Get student's class for this subject
        student_classes = get_student_classes(student_id)
        current_class = None
        for enrollment in student_classes:
            if enrollment.get('class_id', {}).get('subject_id', {}).get('subject_id') == subject_id:
                current_class = enrollment
                break
        
        # Calculate clearance data for this subject
        subject_clearance_percentage = calculate_subject_clearance_percentage(student_id, subject_id)
        subject_clearance_status = calculate_subject_clearance_status(student_id, subject_id)
        
        return render_template("subject.html", 
                             user=user,
                             subject_id=subject_id,
                             subject_name=subject_name,
                             current_class=current_class,
                             subject_books=student_books_for_subject,
                             subject_materials=student_materials_for_subject,
                             subject_clearance_percentage=subject_clearance_percentage,
                             subject_clearance_status=subject_clearance_status,
                             supabase_url=supabase_url, 
                             supabase_anon_key=supabase_anon_key)

    # ===============================
    # API ENDPOINTS FOR AJAX REQUESTS
    # ===============================
    
    @app.route("/api/search/students")
    @verify_supabase_token
    def api_search_students():
        """Search students by name or ID"""
        search_term = request.args.get('q', '')
        if len(search_term) < 2:
            return jsonify([])
        
        students = search_students(search_term)
        return jsonify(students)
    
    @app.route("/api/student/<student_id>/financial")
    @verify_supabase_token
    def api_student_financial(student_id):
        """Get financial details for a specific student"""
        financial_record = get_financial_record(student_id)
        financial_overview = get_student_financial_overview(student_id)
        return jsonify({
            'financial_record': financial_record,
            'financial_overview': financial_overview
        })
    
    @app.route("/api/update/book/<book_id>/return", methods=['POST'])
    @verify_supabase_token
    def api_update_book_return(book_id):
        """Mark a book as returned or not returned"""
        from supabase_client import update_book_status
        data = request.get_json()
        returned = data.get('returned', False)
        
        result = update_book_status(book_id, returned)
        if result:
            return jsonify({'success': True, 'message': 'Book status updated'})
        else:
            return jsonify({'success': False, 'message': 'Failed to update book status'}), 400
    
    @app.route("/api/update/material/<material_id>/return", methods=['POST'])
    @verify_supabase_token
    def api_update_material_return(material_id):
        """Mark a material as returned or not returned"""
        from supabase_client import update_material_status
        data = request.get_json()
        returned = data.get('returned', False)
        
        result = update_material_status(material_id, returned)
        if result:
            return jsonify({'success': True, 'message': 'Material status updated'})
        else:
            return jsonify({'success': False, 'message': 'Failed to update material status'}), 400
    
    @app.route("/api/update/financial/<student_id>", methods=['POST'])
    @verify_supabase_token
    def api_update_financial(student_id):
        """Update financial record for a student"""
        from supabase_client import update_financial_record
        data = request.get_json()
        
        # Only allow updates to specific fields
        allowed_updates = {}
        if 'amount_paid' in data:
            allowed_updates['amount_paid'] = float(data['amount_paid'])
        if 'balance' in data:
            allowed_updates['balance'] = float(data['balance'])
        if 'status' in data:
            allowed_updates['status'] = data['status']
        
        if not allowed_updates:
            return jsonify({'success': False, 'message': 'No valid updates provided'}), 400
        
        result = update_financial_record(student_id, allowed_updates)
        if result:
            return jsonify({'success': True, 'message': 'Financial record updated'})
        else:
            return jsonify({'success': False, 'message': 'Failed to update financial record'}), 400

    # Debug routes for testing hall functionality
    @app.route("/debug/hall/<hall_id>")
    def debug_hall(hall_id):
        """Debug hall data for a specific hall_id"""
        hall_info = get_hall_head_by_id(hall_id)
        hall_students = get_students_by_hall_with_clearance(hall_id)
        hall_rooms = get_rooms_by_hall(hall_id)
        return {
            'hall_id': hall_id,
            'hall_info': hall_info,
            'students_count': len(hall_students),
            'students_data': hall_students,
            'rooms_count': len(hall_rooms) if hall_rooms else 0,
            'rooms_data': hall_rooms
        }
    
    @app.route("/debug/all_halls")
    def debug_all_halls():
        """Debug all hall heads in the database"""
        try:
            result = supabase.table('hall_heads').select('*').execute()
            return {
                'hall_heads': result.data,
                'count': len(result.data)
            }
        except Exception as e:
            return {'error': str(e)}

    return app


app = create_app()



if __name__ == "__main__":
    app.run(debug=True)