"""
ECLARI - Enhanced Clearance System for Academic Resource Integration

A comprehensive Flask web application for managing academic clearance processes.
This system handles student clearance tracking across multiple departments:
- Academic (Teachers) - subject-based book and material returns
- Financial (Finance Staff) - tuition and fee payments  
- Residential (Hall Staff) - dormitory clearance and room assignments
- Laboratory (Lab Staff) - science equipment and materials
- Sports (Coaches) - PE equipment and sports materials

Key Features:
- Role-based authentication with Supabase integration
- Real-time clearance percentage calculations
- Staff dashboards for managing their respective clearance areas
- Student dashboard for tracking personal clearance progress
- API endpoints for dynamic frontend interactions

Built with Flask 3.x, Supabase for backend services, and modern web technologies.
"""

# ===== CORE IMPORTS =====
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
from datetime import datetime
import os
from dotenv import load_dotenv

# ===== LOCAL IMPORTS =====
# Our custom modules for database operations and business logic
from supabase_client import (
    supabase, supabase_url, supabase_anon_key,
    # Student data functions
    get_student_classes, get_student_books, get_student_materials, 
    get_student_financial_overview, get_student_room,
    # Teacher data functions  
    get_teacher_classes, get_students_in_class, get_all_subjects, get_books_by_subject,
    # Finance data functions
    get_all_financial_records, get_all_students, get_financial_record,
    # Hall data functions
    get_hall_head_by_id, get_rooms_by_hall, get_students_by_hall_with_clearance,
    # Lab/Coach data functions
    get_materials_by_subject, get_all_materials,
    # Clearance calculation functions
    calculate_subject_clearance_percentage, calculate_subject_clearance_status,
    calculate_overall_clearance_percentage, calculate_overall_clearance_status,
    # Search and utility functions
    search_students
)

# Core Flask imports for web framework functionality
from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify

# Supabase client and data access functions
from supabase_client import supabase
from supabase_client import (
    # Student data functions - getting personal info, classes, books, materials
    get_student_by_id, get_student_classes, get_student_books, get_student_materials,
    get_student_financial_overview, get_student_room, 
    
    # Teacher data functions - getting teacher info and their classes
    get_teacher_by_id, get_teacher_classes, get_students_in_class, 
    
    # Academic resources - books and materials by subject
    get_books_by_subject, get_materials_by_subject, get_all_materials, get_all_subjects,
    
    # Financial data - records and overviews for finance staff
    get_all_financial_records, get_financial_record,
    
    # Hall management - hall heads, rooms, and student assignments
    get_hall_head_by_id, get_rooms_by_hall, get_all_rooms,
    
    # General data access - all students, teachers, search functionality
    get_all_students, get_all_teachers, search_students,
    
    # Clearance calculations - the heart of the system!
    calculate_subject_clearance_percentage, calculate_subject_clearance_status,
    calculate_overall_clearance_percentage, calculate_overall_clearance_status,
    get_students_by_hall_with_clearance
)

# Standard library imports
import os
import jwt  # JSON Web Token handling for authentication
from functools import wraps  # For creating decorators
from dotenv import load_dotenv  # Environment variable management

# Load environment variables from .env file
# This includes Supabase credentials and Flask secret key
load_dotenv()

def create_app() -> Flask:
    """
    Main Flask application factory.
    
    Creates and configures the Flask app with all routes, authentication,
    and dashboard functionality. This is where the magic happens!
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Set up secret key for session management and security
    # In production, this should be a strong, randomly generated key
    app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-change-this')
    
    # Supabase configuration for frontend JavaScript
    # These are safe to expose to the client (anon key has limited permissions)
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')
    
def verify_supabase_token(f):
    """
    Decorator to verify Supabase authentication and populate session with user data.
    
    This is the CRITICAL security layer that:
    1. Validates the user's authentication token with Supabase
    2. Looks up the user's role in our database 
    3. Populates the session with fresh user data
    4. Prevents role confusion through aggressive session clearing
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Step 1: Get authentication token from cookies
            token = request.cookies.get('supabase-token')
            
            if not token:
                # No token = not authenticated, send to login
                flash('Please log in to access this page.', 'info')
                return redirect(url_for('login'))
            
            # Step 2: Verify token with Supabase and get user ID
            try:
                # This calls Supabase's API to validate the JWT token
                response = supabase.auth.get_user(token)
                
                if not response.user:
                    # Token is invalid or expired
                    flash('Your session has expired. Please log in again.', 'warning')
                    # Clear session and redirect to login
                    session.clear()
                    return redirect(url_for('login'))
                    
                # Extract the Supabase user ID (this connects to our tables)
                auth_uid = response.user.id
                
            except Exception as token_error:
                # Token verification failed (network issues, invalid token, etc.)
                print(f"Token verification error: {token_error}")
                flash('Authentication error. Please log in again.', 'error')
                session.clear()
                return redirect(url_for('login'))
            
            # Step 3: Get user data from our database tables
            # CRITICAL: Always use fresh database lookup, never trust cached session data
            if True:  # Force fresh lookup every time to prevent role confusion
                # This checks our database tables (students, teachers, etc.)
                user_data = get_user_data_by_auth_uid(auth_uid)
                
                if not user_data:
                    # User authenticated with Supabase but not found in our tables
                    # This shouldn't happen in normal operation
                    flash('User not found in system. Please contact administrator.', 'error')
                    return redirect(url_for('login'))
                
                # DEBUG: Always log the role detection for troubleshooting
                print(f"DEBUG AUTH: User {user_data.get('first_name')} {user_data.get('last_name')} detected as {user_data.get('role')} (auth_uid: {auth_uid})")
                
                # Check for role mismatches BEFORE updating session
                # This prevents stale session data from causing role confusion
                cached_user = session.get('user', {})
                if cached_user.get('auth_uid') == auth_uid:
                    if cached_user.get('role') != user_data.get('role'):
                        # Role has changed - clear session completely
                        print(f"DEBUG: Role mismatch detected for {auth_uid}. Cached: {cached_user.get('role')}, Fresh: {user_data.get('role')}")
                        session.clear()
                    else:
                        # Same user, same role - but force refresh session anyway to prevent any caching issues
                        print(f"DEBUG: Refreshing session for {user_data.get('role')} user {user_data.get('first_name')}")
                        session.clear()
                
                # Store user information in the session for this request
                # Always use the fresh data from database lookup
                session['user'] = user_data
                session.permanent = True  # Keep session active longer
                
            # Step 4: Continue to the protected route
            return f(*args, **kwargs)
            
        except Exception as e:
            # Catch-all error handler for any authentication issues
            print(f"Authentication decorator error: {e}")
            flash('Authentication system error. Please try logging in again.', 'error')
            # Clear session completely to force fresh authentication
            session.clear()
            return redirect(url_for('login'))
    
    return decorated_function

def get_user_data_by_auth_uid(auth_uid):
    """
    Look up user data across all role tables using Supabase Auth UID.
    
    This function is crucial for our role-based system! It checks each
    role table (students, teachers, hall_heads, finance_staff) to find
    where this authenticated user belongs.
    
    Args:
        auth_uid (str): The unique user ID from Supabase Auth
        
    Returns:
        dict: User data with role info, or None if not found
    """
    try:
        # Check students table first (most common users)
        student = supabase.table('students').select('*').eq('auth_uid', auth_uid).execute()
        if student.data:
            user = student.data[0]
            return {
                'id': user['student_id'],
                'auth_uid': auth_uid,
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'role': 'student',
                'year_group': user.get('year_group')  # Year group for academic tracking
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
        
        # Check hall heads table (residential staff)
        hall_head = supabase.table('hall_heads').select('*').eq('auth_uid', auth_uid).execute()
        if hall_head.data:
            user = hall_head.data[0]
            return {
                'id': user['hall_id'],
                'auth_uid': auth_uid,
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'role': 'hall',
                'hall_name': user.get('hall_name')  # Which hall they manage
            }
        
        # Check finance_staff table (handles all financial clearance)
        finance_staff = supabase.table('finance_staff').select('*').eq('auth_uid', auth_uid).execute()
        if finance_staff.data:
            user = finance_staff.data[0]
            return {
                'id': user['finance_id'],
                'auth_uid': auth_uid,
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'role': 'finance'  # Special role for financial clearance management
            }
        
        # Check lab_staff table (handles science lab equipment)
        lab_staff = supabase.table('lab_staff').select('*').eq('auth_uid', auth_uid).execute()
        if lab_staff.data:
            user = lab_staff.data[0]
            return {
                'id': user['lab_staff_id'],
                'auth_uid': auth_uid,
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'role': 'lab',
                'specialization': user.get('specialization')  # Physics, Chemistry, Biology, or All
            }
        
        # Check coaches table (handles sports equipment)
        coach = supabase.table('coaches').select('*').eq('auth_uid', auth_uid).execute()
        if coach.data:
            user = coach.data[0]
            return {
                'id': user['coach_id'],
                'auth_uid': auth_uid,
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'role': 'coach',
                'sport': user.get('sport')  # Football, Basketball, Athletics, etc.
            }
        
        # User authenticated but not found in any role table
        return None
        
    except Exception as e:
        # Log the error for debugging but don't expose details to user
        print(f"Error getting user data: {e}")
        return None


def create_app():
    """
    Application factory function for creating the Flask app instance.
    
    This function sets up all the routes, configurations, and middleware
    needed for the Eclari application to run properly.
    
    Returns:
        Flask: Configured Flask application instance
    """
    # Initialize Flask application with custom settings
    app = Flask(__name__)
    
    # Load environment variables for configuration
    load_dotenv()
    
    # Set Flask configuration
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_TYPE'] = 'filesystem'
    
    # ===== ROUTE DEFINITIONS =====
    # Main application routes handling different pages and functionality

    @app.route("/")
    def home():
        """Homepage route - shows the main Eclari landing page."""
        return render_template("index.html")

    @app.route("/login")
    def login():
        """
        Login page route with smart redirect functionality.
        
        If user is already authenticated, automatically redirects them
        to their appropriate dashboard based on their role.
        """
        # Check if user is already authenticated
        token = request.cookies.get('supabase-token')
        if token:
            try:
                # Verify token and get user info
                response = supabase.auth.get_user(token)
                if response.user:
                    # User is already logged in, get their role from our database
                    auth_uid = response.user.id
                    user_data = get_user_data_by_auth_uid(auth_uid)
                    
                    if user_data:
                        # Smart redirect: send them straight to their dashboard
                        return redirect(url_for('dashboard', role=user_data['role']))
            except Exception as e:
                # Token is invalid or expired, clear it and continue to login
                print(f"Login redirect error: {e}")
                response = redirect(url_for('login'))
                response.set_cookie('supabase-token', '', expires=0, path='/')
                response.set_cookie('user-info', '', expires=0, path='/')
                return response
        
        # Show login page with Supabase configuration
        # These config values are passed to frontend JavaScript for auth
        return render_template("login.html", 
                             supabase_url=supabase_url, 
                             supabase_anon_key=supabase_anon_key)

    @app.route("/auto-redirect")
    @verify_supabase_token
    def auto_redirect():
        """
        Smart redirect route that automatically sends users to their correct dashboard.
        
        This is called after login to ensure users go to the right place based on 
        their actual role in the database (not what they selected on the login form).
        """
        user = session.get('user', {})
        role = user.get('role', 'student')
        
        print(f"Auto-redirect: User {user.get('first_name')} {user.get('last_name')} has role {role}")
        
        # Redirect to the appropriate dashboard
        return redirect(url_for('dashboard', role=role))

    @app.route("/dashboard/<role>")
    @verify_supabase_token
    def dashboard(role):
        """
        Main dashboard route - the heart of the application!
        
        This handles role-based dashboards for all user types:
        - Students: See their clearance status, classes, financial info
        - Teachers: Manage their classes and students
        - Hall Staff: Monitor students in their hall
        - Finance Staff: Handle financial clearance for all students
        
        Args:
            role (str): The user role (student, teacher, hall, finance, etc.)
            
        Returns:
            Rendered template with role-specific data
        """
        # Get user info from session (set by authentication decorator)
        user = session.get('user', {})
        user_role = user.get('role', 'student')
        
        # Security check: ensure user can only access their own dashboard
        # This prevents students from accessing teacher dashboards by changing the URL
        if user_role != role and role != 'student':  # Allow fallback to student
            flash(f'Access denied. You are registered as a {user_role}.', 'error')
            return redirect(url_for('dashboard', role=user_role))
        
        # Base data that all dashboards need
        dashboard_data = {
            'user': user,  # User info for header display
            'supabase_url': supabase_url,  # For frontend API calls
            'supabase_anon_key': supabase_anon_key  # For frontend API calls
        }
        
        # ===== STUDENT DASHBOARD =====
        # The most complex dashboard with clearance tracking
        if role == 'student':
            student_id = user.get('id')
            student_classes = get_student_classes(student_id)
            
            # Calculate clearance percentages for each subject
            # This is the core functionality students care about most!
            for enrollment in student_classes:
                subject_id = enrollment.get('class_id', {}).get('subject_id', {}).get('subject_id')
                if subject_id:
                    # Add percentage and status for each subject
                    enrollment['clearance_percentage'] = calculate_subject_clearance_percentage(student_id, subject_id)
                    enrollment['clearance_status'] = calculate_subject_clearance_status(student_id, subject_id)
            
            # Compile comprehensive student data for dashboard
            dashboard_data.update({
                'student_classes': student_classes,  # Classes and clearance status
                'student_books': get_student_books(student_id),  # Books to return
                'student_materials': get_student_materials(student_id),  # Lab materials status
                'financial_overview': get_student_financial_overview(student_id),  # Financial status
                'room_assignment': get_student_room(student_id),  # Hall assignment
                'overall_clearance_percentage': calculate_overall_clearance_percentage(student_id),  # Overall progress
                'overall_clearance_status': calculate_overall_clearance_status(student_id)  # Overall status
            })
        
        # ===== TEACHER DASHBOARD =====
        # Teachers manage their classes and track student progress
        elif role == 'teacher':
            teacher_id = user.get('id')
            teacher_classes = get_teacher_classes(teacher_id)
            dashboard_data.update({
                'teacher_classes': teacher_classes,  # Classes they teach
                'all_subjects': get_all_subjects()  # For reference
            })
            
            # Enrich each class with student lists and resources
            for class_info in teacher_classes:
                class_info['students'] = get_students_in_class(class_info['class_id'])
                if class_info.get('subject_id'):
                    # Add books for this subject
                    class_info['books'] = get_books_by_subject(class_info['subject_id']['subject_id'])
        
        # ===== FINANCE DASHBOARD =====
        # Finance staff handle all student financial clearance
        elif role == 'finance':
            dashboard_data.update({
                'financial_records': get_all_financial_records(),  # All financial data
                'all_students': get_all_students()  # Student directory for lookups
            })
        
        # ===== HALL DASHBOARD =====
        # Hall staff manage residential clearance for their hall
        elif role == 'hall':
            hall_id = user.get('id')
            hall_info = get_hall_head_by_id(hall_id)
            dashboard_data.update({
                'hall_rooms': get_rooms_by_hall(hall_id),  # Rooms in this hall
                'hall_info': hall_info,  # Hall details
                'hall_students': get_students_by_hall_with_clearance(hall_id),  # Students with clearance status
                'hall_name': hall_info.get('hall_name') if hall_info else 'Unknown Hall'
            })
        
        # ===== LAB DASHBOARD =====
        # Lab staff manage science equipment and materials
        elif role == 'lab':
            dashboard_data.update({
                'materials': get_materials_by_subject('SCI'),  # Science materials only
                'dashboard_title': 'Lab Equipment',
                'item_type': 'Equipment',
                'table_title': 'Laboratory Equipment Tracking',
                'category_label': 'Lab Subject',
                'item_label': 'Equipment Name',
                'subject_code': 'SCI',
                'empty_icon': '🔬',
                'empty_message': 'No laboratory equipment found in the system.'
            })
        
        # ===== COACH DASHBOARD =====
        # Sports coaches manage PE equipment and sports materials
        elif role == 'coach':
            dashboard_data.update({
                'materials': get_materials_by_subject('PE'),  # PE/Sports materials only
                'dashboard_title': 'Sports Equipment',
                'item_type': 'Equipment',
                'table_title': 'Sports Equipment Tracking',
                'category_label': 'Sports Category',
                'item_label': 'Equipment Name',
                'subject_code': 'PE',
                'empty_icon': '⚽',
                'empty_message': 'No sports equipment found in the system.'
            })
        
        # ===== TEMPLATE ROUTING =====
        # Map each role to its corresponding HTML template
        template_map = {
            'student': 'student.html',              # Student clearance dashboard
            'teacher': 'teacher.html',              # Teacher class management
            'finance': 'finance.html',              # Financial clearance management
            'hall': 'hall.html',                    # Hall residential management
            'coach': 'materials_dashboard.html',    # Sports equipment (shared template)
            'lab': 'materials_dashboard.html'       # Lab equipment (shared template)
        }
        
        # Get the appropriate template, defaulting to student if role not found
        template = template_map.get(role, 'student.html')
        
        # Render the template with all the role-specific data
        return render_template(template, **dashboard_data)

    @app.route("/logout")
    def logout():
        """
        Handle user logout - clean up all session data and cookies.
        
        This ensures a complete logout by clearing both server-side session
        and client-side authentication cookies.
        """
        # Clear Flask session data
        session.clear()
        
        # Redirect to login page and clear Supabase authentication cookies
        response = redirect(url_for('login'))
        response.set_cookie('supabase-token', '', expires=0, path='/')
        response.set_cookie('user-info', '', expires=0, path='/')
        
        flash('You have been logged out successfully.', 'info')
        return response

    # ===== SESSION MANAGEMENT ROUTES =====
    # New route to completely reset user session - useful for debugging auth issues
    @app.route('/reset-session')
    def reset_session():
        """Completely clear all session data and force fresh authentication"""
        session.clear()
        # Also clear any potential server-side cache by forcing a new session ID
        session.permanent = False
        session.modified = True
        
        flash('Session completely reset. Please log in again.', 'info')
        return redirect(url_for('login'))

    # Debug route to check current session state
    @app.route('/debug/session')
    def debug_session():
        """Show current session contents for debugging"""
        if 'debug' not in session:
            session['debug'] = True
        
        session_info = {
            'session_keys': list(session.keys()),
            'user_data': session.get('user', 'None'),
            'session_id': session.get('_id', 'No ID'),
            'permanent': session.permanent,
            'modified': session.modified
        }
        
        return jsonify(session_info)

    # Enhanced debug route with comprehensive authentication testing
    @app.route('/debug/auth-test')
    def debug_auth_test():
        """Comprehensive authentication test for all user roles"""
        try:
            # Get current Supabase user
            user = supabase.auth.get_user()
            if not user.user:
                return jsonify({"error": "No authenticated user", "instructions": "Please log in first"})
            
            auth_uid = user.user.id
            
            # Test role detection logic step by step
            auth_test_results = {
                "current_auth_uid": auth_uid,
                "timestamp": str(datetime.now()),
                "test_steps": []
            }
            
            # Step 1: Check each table individually
            tables_check = {}
            for table_name in ['students', 'teachers', 'hall_heads', 'finance_staff']:
                try:
                    result = supabase.table(table_name).select('*').eq('auth_uid', auth_uid).execute()
                    tables_check[table_name] = {
                        "found": len(result.data) > 0,
                        "count": len(result.data),
                        "data": result.data[0] if result.data else None
                    }
                except Exception as e:
                    tables_check[table_name] = {"error": str(e)}
            
            auth_test_results["table_checks"] = tables_check
            
            # Step 2: Test role detection function
            try:
                detected_user = get_user_data_by_auth_uid(auth_uid)
                auth_test_results["role_detection"] = {
                    "success": detected_user is not None,
                    "detected_role": detected_user.get('role') if detected_user else None,
                    "detected_user": detected_user
                }
            except Exception as e:
                auth_test_results["role_detection"] = {"error": str(e)}
            
            # Step 3: Check current session state
            auth_test_results["session_state"] = {
                "session_exists": 'user' in session,
                "session_user": session.get('user', None),
                "session_keys": list(session.keys())
            }
            
            # Step 4: Generate recommendations
            recommendations = []
            
            # Check for multiple role assignments (shouldn't happen)
            role_count = sum(1 for table, data in tables_check.items() if data.get('found', False))
            if role_count == 0:
                recommendations.append("❌ User not found in any role table - check database setup")
            elif role_count > 1:
                recommendations.append("⚠️ User found in multiple role tables - data integrity issue")
            else:
                recommendations.append("✅ User found in exactly one role table - correct setup")
            
            # Check session consistency
            if auth_test_results["session_state"]["session_exists"]:
                session_role = session.get('user', {}).get('role')
                detected_role = auth_test_results["role_detection"].get("detected_role")
                if session_role == detected_role:
                    recommendations.append("✅ Session role matches detected role")
                else:
                    recommendations.append(f"⚠️ Session role ({session_role}) doesn't match detected role ({detected_role})")
            else:
                recommendations.append("ℹ️ No session data - will be populated on next protected route access")
            
            auth_test_results["recommendations"] = recommendations
            
            return jsonify(auth_test_results)
            
        except Exception as e:
            return jsonify({"error": f"Auth test failed: {str(e)}"})

    @app.route('/debug/force-refresh')
    def debug_force_refresh():
        """Force complete session refresh and redirect to appropriate dashboard"""
        try:
            # Clear everything
            session.clear()
            
            # Get current user
            user = supabase.auth.get_user()
            if not user.user:
                flash('No authenticated user found.', 'error')
                return redirect(url_for('login'))
            
            auth_uid = user.user.id
            
            # Force fresh lookup
            user_data = get_user_data_by_auth_uid(auth_uid)
            
            if user_data:
                # Force session update with fresh data
                session['user'] = user_data
                session.permanent = True
                flash(f'Session refreshed! You are logged in as {user_data["role"]}: {user_data["first_name"]} {user_data["last_name"]}', 'success')
                
                # Redirect to appropriate dashboard
                role = user_data['role']
                return redirect(url_for('dashboard', role=role))
            else:
                flash('User not found in any role table.', 'error')
                return redirect(url_for('login'))
                
        except Exception as e:
            flash(f'Error during refresh: {str(e)}', 'error')
            return redirect(url_for('login'))

    @app.route("/debug/role")
    @verify_supabase_token  
    def debug_role():
        """Debug route to check current user role detection"""
        user = session.get('user', {})
        token = request.cookies.get('supabase-token')
        
        debug_info = {
            'session_user': user,
            'token_present': bool(token)
        }
        
        if token:
            try:
                response = supabase.auth.get_user(token)
                if response.user:
                    auth_uid = response.user.id
                    fresh_user_data = get_user_data_by_auth_uid(auth_uid)
                    debug_info.update({
                        'auth_uid': auth_uid,
                        'fresh_lookup': fresh_user_data,
                        'role_match': user.get('role') == fresh_user_data.get('role') if fresh_user_data else False
                    })
            except Exception as e:
                debug_info['error'] = str(e)
                
        return f"<pre>{debug_info}</pre>"

    @app.route("/fix-gon-role")
    def fix_gon_role():
        """Emergency fix for Gon's role - forces finance role assignment"""
        # Get token to verify it's actually Gon
        token = request.cookies.get('supabase-token')
        if not token:
            return redirect(url_for('login'))
            
        try:
            response = supabase.auth.get_user(token)
            if response.user and response.user.id == 'b9906ec1-fca7-41f3-8ac6-caa6b9bc9cd9':
                # This is Gon - force set as finance
                session.clear()  # Clear any cached data
                session['user'] = {
                    'id': 'FIN002',
                    'auth_uid': 'b9906ec1-fca7-41f3-8ac6-caa6b9bc9cd9',
                    'first_name': 'Gon',
                    'last_name': 'Freecs',
                    'role': 'finance'
                }
                flash('Role fixed! You are now logged in as Finance Staff.', 'success')
                return redirect(url_for('dashboard', role='finance'))
            else:
                flash('This fix is only for Gon Freecs.', 'error')
                return redirect(url_for('login'))
        except Exception as e:
            print(f"Fix route error: {e}")
            return redirect(url_for('login'))

    @app.route("/force-logout")
    def force_logout():
        """Force complete logout - clears all session data and cookies"""
        # Clear Flask session
        session.clear()
        
        # Create response with redirect to login
        response = redirect(url_for('login'))
        
        # Clear all possible authentication cookies
        response.set_cookie('supabase-token', '', expires=0, path='/')
        response.set_cookie('user-info', '', expires=0, path='/')
        response.set_cookie('sb-access-token', '', expires=0, path='/')
        response.set_cookie('sb-refresh-token', '', expires=0, path='/')
        
        # Add cache control headers to prevent caching
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        flash('Forced logout completed. Please log in again.', 'info')
        return response

    # ===== LEGACY ROUTE REDIRECTS =====
    # These maintain compatibility with old URLs while using new dashboard system
    
    @app.route("/student")
    @verify_supabase_token
    def student():
        """Legacy route - redirect to new student dashboard."""
        return redirect(url_for('dashboard', role='student'))

    @app.route("/teacher")
    @verify_supabase_token
    def teacher():
        """Legacy route - redirect to new teacher dashboard."""
        return redirect(url_for('dashboard', role='teacher'))

    @app.route("/finance")
    @verify_supabase_token
    def finance():
        """Legacy route - redirect to new finance dashboard."""
        return redirect(url_for('dashboard', role='finance'))

    @app.route("/hall")
    @verify_supabase_token
    def hall():
        """Legacy route - redirect to new hall dashboard."""
        return redirect(url_for('dashboard', role='hall'))

    @app.route("/coach")
    @verify_supabase_token
    def coach():
        """Legacy route - redirect to new coach dashboard."""
        return redirect(url_for('dashboard', role='coach'))

    @app.route("/lab")
    @verify_supabase_token
    def lab():
        """Legacy route - redirect to new lab dashboard."""
        return redirect(url_for('dashboard', role='lab'))

    # ===== SPECIALIZED PAGES =====
    # These provide focused views for specific functionality

    @app.route("/subject")
    @app.route("/subject/<subject_id>")
    @verify_supabase_token
    def subject(subject_id=None):
        """
        Subject-specific clearance page for detailed view.
        
        Shows detailed clearance information for a single subject,
        including books, materials, and clearance requirements.
        """
        user = session.get('user', {})
        student_id = user.get('id')
        
        if not subject_id:
            # No subject specified, send them back to main dashboard
            return redirect(url_for('dashboard', role=user.get('role', 'student')))
        
        # Get human-readable subject name from URL parameters
        subject_name = request.args.get('name', subject_id)
        
        # Filter student data to show only this subject's items
        student_books_for_subject = []
        student_materials_for_subject = []
        
        # Get all books and filter to this subject only
        all_books = get_student_books(student_id)
        student_books_for_subject = [book for book in all_books 
                                   if book.get('subject_id', {}).get('subject_id') == subject_id]
        
        # Get all materials and filter to this subject only
        all_materials = get_student_materials(student_id)
        student_materials_for_subject = [material for material in all_materials 
                                       if material.get('subject_id') == subject_id]
        
        # Find the student's enrollment in this subject
        student_classes = get_student_classes(student_id)
        current_class = None
        for enrollment in student_classes:
            if enrollment.get('class_id', {}).get('subject_id', {}).get('subject_id') == subject_id:
                current_class = enrollment
                break
        
        # Calculate subject-specific clearance metrics
        subject_clearance_percentage = calculate_subject_clearance_percentage(student_id, subject_id)
        subject_clearance_status = calculate_subject_clearance_status(student_id, subject_id)
        
        # Render subject page with all the filtered data
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

    # ===== API ENDPOINTS =====
    # These provide JSON data for AJAX requests from the frontend
    
    @app.route("/api/search/students")
    @verify_supabase_token
    def api_search_students():
        """
        Search students by name or ID for autocomplete functionality.
        Used by staff dashboards for quick student lookups.
        """
        search_term = request.args.get('q', '')
        if len(search_term) < 2:
            # Don't search for very short terms (performance)
            return jsonify([])
        
        students = search_students(search_term)
        return jsonify(students)
    
    @app.route("/api/student/<student_id>/financial")
    @verify_supabase_token
    def api_student_financial(student_id):
        """
        Get detailed financial information for a specific student.
        Used by finance staff for detailed financial review.
        """
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
        from supabase_client import update_financial_record, get_financial_record
        data = request.get_json()
        
        # Get current financial record to calculate values
        current_record = get_financial_record(student_id)
        if not current_record:
            return jsonify({'success': False, 'message': 'Financial record not found'}), 404
        
        tuition_due = current_record.get('tuition_due', 0)
        
        # Only allow updates to specific fields
        allowed_updates = {}
        
        # If amount_paid is provided, calculate balance automatically
        if 'amount_paid' in data:
            amount_paid = float(data['amount_paid'])
            allowed_updates['amount_paid'] = amount_paid
            allowed_updates['balance'] = tuition_due - amount_paid
        
        # Allow direct balance updates (for manual adjustments)
        if 'balance' in data and 'amount_paid' not in data:
            balance = float(data['balance'])
            allowed_updates['balance'] = balance
            # Calculate amount_paid based on balance
            allowed_updates['amount_paid'] = tuition_due - balance
        
        # Update status if provided
        if 'status' in data:
            allowed_updates['status'] = data['status']
        
        if not allowed_updates:
            return jsonify({'success': False, 'message': 'No valid updates provided'}), 400
        
        result = update_financial_record(student_id, allowed_updates)
        if result:
            return jsonify({'success': True, 'message': 'Financial record updated', 'data': result})
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
    
    # ===== DEBUG ROUTES =====
    # These routes help with development and debugging
    # Should be removed in production!
    
    @app.route("/debug/all_halls")
    def debug_all_halls():
        """Debug endpoint to view all hall heads in the database."""
        try:
            result = supabase.table('hall_heads').select('*').execute()
            return {
                'hall_heads': result.data,
                'count': len(result.data)
            }
        except Exception as e:
            return {'error': str(e)}

    return app


# ===== APPLICATION INITIALIZATION =====
# Create the Flask app instance
app = create_app()

# Development server runner  
# In production, use a proper WSGI server like gunicorn
if __name__ == "__main__":
    # Use PORT environment variable for cloud deployment (e.g., Render)
    # Falls back to 5000 for local development
    port = int(os.environ.get("PORT", 5000))
    # host="0.0.0.0" allows external connections (required for cloud deployment)
    # debug should be False in production for security
    app.run(host="0.0.0.0", port=port, debug=True)