from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from supabase_client import supabase
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
                    # User is already logged in, redirect to dashboard
                    role = response.user.raw_user_meta_data.get('role', 'student') if response.user.raw_user_meta_data else 'student'
                    return redirect(url_for('dashboard', role=role))
            except Exception:
                pass  # Token is invalid, continue to login page
        
        return render_template("login.html", 
                             supabase_url=supabase_url, 
                             supabase_anon_key=supabase_anon_key)

    @app.route("/dashboard/<role>")
    @verify_supabase_token
    def dashboard(role):
        """Role-based dashboard routing"""
        user = session.get('user', {})
        user_role = user.get('role', 'student')
        
        # Ensure user can only access their designated dashboard
        if user_role != role and role != 'student':  # Allow fallback to student
            flash(f'Access denied. You are registered as a {user_role}.', 'error')
            return redirect(url_for('dashboard', role=user_role))
        
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
        return render_template(template, user=user)

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
    @verify_supabase_token
    def subject():
        return render_template("subject.html")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)