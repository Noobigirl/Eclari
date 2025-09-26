from flask import Flask, render_template, redirect, url_for
from supabase_client import supabase

def create_app() -> Flask:
    app = Flask(__name__)

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/login")
    def login():
        return render_template("login.html")

    @app.route("/student")
    def student():
        return render_template("student.html")

    @app.route("/teacher")
    def teachers_redirect():
        """Redirect to test teacher for now"""
        return redirect(url_for('teacher', teacher_id=3434))

    @app.route("/teacher/<int:teacher_id>")
    def teacher(teacher_id):
        try:
            print(f"Looking for teacher with ID: {teacher_id}")
            
            # Get teacher info
            teacher_response = supabase.table("teachers").select("*").eq("teacher_id", teacher_id).execute()
            
            if not teacher_response.data:
                return f"Teacher with ID {teacher_id} not found", 404
            
            teacher = teacher_response.data[0]
            print(f"Teacher found: {teacher['first_name']} {teacher['last_name']}")

            # Get classes taught by this teacher with subject information
            classes_response = supabase.table("classes").select("""
                class_id,
                class_name,
                year_group,
                max_students,
                subjects (
                    subject_id,
                    subject_name
                )
            """).eq("teacher_id", teacher_id).execute()
            
            classes = classes_response.data or []
            print(f"Classes found: {len(classes)}")

            # Get all students enrolled in these classes with their items
            table_data = []
            all_students = set()  # Use set to avoid duplicates
            
            for class_info in classes:
                # Get students enrolled in this class
                enrollments_response = supabase.table("student_classes").select("""
                    students (
                        student_id,
                        first_name,
                        last_name,
                        year_group
                    )
                """).eq("class_id", class_info["class_id"]).eq("status", "Active").execute()
                
                enrollments = enrollments_response.data or []
                
                for enrollment in enrollments:
                    student = enrollment["students"]
                    if student:
                        student_id = student["student_id"]
                        student_name = f"{student['first_name']} {student['last_name']}"
                        all_students.add(student_id)
                        
                        # Get books for this student in this subject
                        books_response = supabase.table("books").select("*").eq("student_id", student_id).eq("subject_id", class_info["subjects"]["subject_id"]).execute()
                        books = books_response.data or []
                        
                        # Get materials for this student in this subject  
                        materials_response = supabase.table("materials").select("*").eq("student_id", student_id).eq("subject_id", class_info["subjects"]["subject_id"]).execute()
                        materials = materials_response.data or []
                        
                        # Add books to table
                        for book in books:
                            table_data.append({
                                'class_name': class_info["class_name"],
                                'student_name': student_name,
                                'subject': class_info["subjects"]["subject_name"],
                                'item': f"Book: {book['book_id']}",
                                'returned': book['returned']
                            })
                        
                        # Add materials to table
                        for material in materials:
                            table_data.append({
                                'class_name': class_info["class_name"],
                                'student_name': student_name,
                                'subject': class_info["subjects"]["subject_name"],
                                'item': f"Material: {material['material_name']}",
                                'returned': material['returned']
                            })
                        
                        # If no books or materials, still show the student
                        if not books and not materials:
                            table_data.append({
                                'class_name': class_info["class_name"],
                                'student_name': student_name,
                                'subject': class_info["subjects"]["subject_name"],
                                'item': "No items assigned",
                                'returned': None
                            })

            print(f"Table data entries: {len(table_data)}")
            print(f"Unique students: {len(all_students)}")

            return render_template(
                "teacher.html",
                teacher=teacher,
                classes=classes,
                table_data=table_data
            )
            
        except Exception as e:
            print(f"Error in teacher route: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"An error occurred: {str(e)}", 500

    @app.route("/subject")
    def subject():
        return render_template("subject.html")

    @app.route("/finance")
    def finance():
        return render_template("finance.html")

    @app.route("/hall")
    def hall():
        return render_template("hall.html")

    @app.route("/coach")
    def coach():
        return render_template("coach.html")

    @app.route("/lab")
    def lab():
        return render_template("lab.html")

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)