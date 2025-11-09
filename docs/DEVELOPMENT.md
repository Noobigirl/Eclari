# 🛠️ Development Guide

This guide covers everything you need to know to develop and maintain the Eclari clearance system.

## Table of Contents

1. [Development Setup](#development-setup)
2. [Code Structure](#code-structure)
3. [Database Management](#database-management)
4. [Adding New Features](#adding-new-features)
5. [Testing](#testing)
6. [Deployment](#deployment)
7. [Troubleshooting](#troubleshooting)

---

## Development Setup

### First-Time Setup

1. **Clone and setup environment**
```bash
git clone https://github.com/Noobigirl/Eclari.git
cd Eclari

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
npm install
```

2. **Configure Supabase**
- Create a project at supabase.com
- Run migrations from `sql/database_migration_year_groups_SAFE.sql`
- Apply RLS policies from `sql/rls_policies_*.sql`
- Create storage bucket: `clearance-proofs`
- Copy API keys to `.env`

3. **Build and run**
```bash
npm run build
flask run
```

### Daily Development Workflow

```bash
# Activate virtual environment
source .venv/bin/activate

# Start Flask with auto-reload (development mode)
export FLASK_ENV=development
flask run --debug

# In another terminal: Watch and rebuild frontend assets
npm run dev
```

---

## Code Structure

### Backend (`app.py`)

The main Flask application is organized into sections:

1. **Authentication** (`verify_supabase_token` decorator)
   - Validates JWT tokens from Supabase
   - Populates session with user data
   - Prevents role confusion with aggressive session clearing

2. **Route Handlers**
   - Public routes: `/`, `/login`
   - Protected routes: `/dashboard/<role>`, `/subject/<id>`
   - API endpoints: `/api/*`

3. **Dashboard Logic**
   - Each role gets customized data
   - Templates receive role-specific context
   - Clearance calculations happen here

### Database Layer (`supabase_client.py`)

Clean separation of concerns:

```python
# Student functions
get_student_by_id(student_id)
get_student_books(student_id)
get_student_materials(student_id)

# Teacher functions
get_teacher_classes(teacher_id)
get_books_by_subject(subject_id)

# Clearance calculations
calculate_overall_clearance_percentage(student_id)
calculate_subject_clearance_percentage(student_id, subject_id)
```

**Design principle:** One function, one responsibility. Easy to test, easy to maintain.

### Frontend (`src/`)

**`src/auth.js`** - Supabase authentication
- Login/logout flows
- JWT token management
- Role detection

**`src/app.js`** - General app logic
- Shared utilities
- Common UI interactions

**Templates** - Jinja2 with inline JavaScript
- Server-rendered HTML with Flask
- Dynamic interactions with vanilla JS
- No heavy frameworks = fast load times

---

## Database Management

### Schema Overview

**12 main tables:**
- `students`, `teachers`, `hall_heads`, `finance_staff`, `lab_staff`, `coaches` (user roles)
- `classes`, `subjects` (academic structure)
- `books`, `materials` (clearance items)
- `finance` (financial records)
- `rooms` (hall assignments)

**Key relationships:**
- Students → Classes (many-to-many via `student_classes`)
- Books/Materials → Students (one-to-many)
- Classes → Subjects → Teachers
- Rooms → Hall Heads

### Running Migrations

```bash
# In Supabase SQL Editor, run in order:
1. sql/database_migration_year_groups_SAFE.sql  # Schema + data
2. sql/rls_policies_books.sql                    # Book RLS
3. sql/rls_policies_materials.sql                # Material RLS
4. sql/rls_policies_storage.sql                  # Storage RLS
```

### Adding a New Column

Example: Adding `notes` field to `books` table:

```sql
-- 1. Add column
ALTER TABLE books ADD COLUMN notes TEXT;

-- 2. Update Python function
# In supabase_client.py
def get_student_books(student_id):
    result = supabase.table('books').select('''
        *,
        subject_id (subject_id, subject_name),
        notes  -- New field
    ''').eq('student_id', student_id).execute()
    return result.data

-- 3. Update template
<!-- In student.html -->
{% if book.notes %}
  <p>Notes: {{ book.notes }}</p>
{% endif %}
```

---

## Adding New Features

### Example: Adding a "Comments" Feature

**Step 1: Database**
```sql
CREATE TABLE clearance_comments (
    comment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id VARCHAR(50) REFERENCES students(student_id),
    staff_id VARCHAR(50),
    comment TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- RLS Policy
ALTER TABLE clearance_comments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Students can view their comments"
ON clearance_comments FOR SELECT
TO authenticated
USING (student_id = auth.uid());
```

**Step 2: Python Function**
```python
# In supabase_client.py
def get_student_comments(student_id):
    """Get all comments for a student"""
    try:
        result = supabase.table('clearance_comments')\
            .select('*')\
            .eq('student_id', student_id)\
            .order('created_at', desc=True)\
            .execute()
        return result.data
    except Exception as e:
        print(f"Error getting comments: {e}")
        return []

def add_comment(student_id, staff_id, comment):
    """Add a new comment"""
    try:
        result = supabase.table('clearance_comments').insert({
            'student_id': student_id,
            'staff_id': staff_id,
            'comment': comment
        }).execute()
        return result.data
    except Exception as e:
        print(f"Error adding comment: {e}")
        return None
```

**Step 3: Backend Route**
```python
# In app.py
@app.route("/api/comments/<student_id>", methods=['GET', 'POST'])
@verify_supabase_token
def handle_comments(student_id):
    if request.method == 'GET':
        comments = get_student_comments(student_id)
        return jsonify({'success': True, 'comments': comments})
    
    elif request.method == 'POST':
        user = session.get('user', {})
        data = request.get_json()
        comment = data.get('comment')
        
        result = add_comment(student_id, user.get('id'), comment)
        if result:
            return jsonify({'success': True, 'comment': result})
        return jsonify({'success': False}), 400
```

**Step 4: Frontend (in template)**
```html
<!-- In student.html -->
<div class="comments-section">
    <h3>Comments from Staff</h3>
    <div id="commentsContainer"></div>
</div>

<script>
async function loadComments() {
    const response = await fetch('/api/comments/{{ user.id }}');
    const data = await response.json();
    
    const container = document.getElementById('commentsContainer');
    container.innerHTML = data.comments.map(c => `
        <div class="comment">
            <p>${c.comment}</p>
            <small>${new Date(c.created_at).toLocaleDateString()}</small>
        </div>
    `).join('');
}

loadComments();
</script>
```

---

## Testing

### Manual Testing Checklist

**Authentication:**
- [ ] Can log in as each role
- [ ] Session persists across page reloads
- [ ] Logout clears session properly
- [ ] Can't access other roles' dashboards

**Student Flow:**
- [ ] Dashboard shows correct clearance %
- [ ] Subject pages show correct books/materials
- [ ] Y1 can upload photos
- [ ] Y2 can see physical return status
- [ ] PDF exports when 100% cleared

**Staff Flow:**
- [ ] Teachers see only their classes
- [ ] Can approve/reject Y1 photos
- [ ] Can mark Y2 items as returned
- [ ] Finance can update balances
- [ ] Hall can mark rooms cleared

### Debug Tools

**Clearance Debug Script:**
```bash
python -c "
from supabase_client import *
student_id = 'ST001'
print(f'Clearance: {calculate_overall_clearance_percentage(student_id)}%')
print(f'Status: {calculate_overall_clearance_status(student_id)}')
"
```

**Database Quick Queries:**
```bash
# Check a student's clearance items
python -c "
from supabase_client import *
books = get_student_books('ST001')
print(f'Books: {len(books)}, Returned: {sum(1 for b in books if b[\"returned\"])}')
"
```

---

## Deployment

### Production Checklist

**Environment:**
- [ ] Set `FLASK_ENV=production`
- [ ] Use strong `FLASK_SECRET_KEY`
- [ ] Enable HTTPS
- [ ] Set secure cookie flags

**Database:**
- [ ] RLS policies enabled on all tables
- [ ] Storage bucket configured with RLS
- [ ] Indexes created for performance
- [ ] Backup strategy in place

**Frontend:**
- [ ] Run `npm run build` (not `npm run dev`)
- [ ] Minified assets in `static/js/`
- [ ] Images optimized

**Server:**
```bash
# Use gunicorn for production
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app

# Or with systemd service
sudo systemctl start eclari
```

### Environment Variables

Production `.env`:
```env
FLASK_ENV=production
FLASK_SECRET_KEY=<long-random-string>
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=<service-role-key>
SUPABASE_ANON_KEY=<anon-key>
PDF_OWNER_PASSWORD=<secure-password>
```

---

## Troubleshooting

### Common Development Issues

**"Module not found" errors:**
```bash
# Make sure venv is activated
source .venv/bin/activate
pip install -r requirements.txt
```

**Frontend changes not showing:**
```bash
# Rebuild assets
npm run build

# Or use watch mode
npm run dev
```

**Database connection fails:**
- Check `.env` has correct Supabase credentials
- Verify Supabase project is active
- Check internet connection

**Session/auth issues:**
- Clear browser cookies
- Check Supabase JWT secret matches
- Verify RLS policies allow access

### Debug Mode

Enable detailed logging:
```python
# In app.py, after create_app()
app.config['DEBUG'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True

import logging
logging.basicConfig(level=logging.DEBUG)
```

Then check terminal for detailed stack traces.

---

## Code Style Guide

### Python

- Use **descriptive names**: `calculate_overall_clearance_percentage` not `calc_pct`
- **Document functions** with docstrings
- **Handle errors**: Always try/except database calls
- **Log debugging info**: `print(f"[DEBUG] ...")` for troubleshooting

### JavaScript

- Use **const/let**, not var
- **Async/await** for API calls
- **Arrow functions** for callbacks
- **Template literals** for strings with variables

### SQL

- Use **explicit JOINs**, not implicit
- Always specify **column names** in SELECT
- **Parameterize queries** (Supabase does this)
- Add **indexes** for foreign keys

---

## Resources

- **Flask Docs:** https://flask.palletsprojects.com/
- **Supabase Docs:** https://supabase.com/docs
- **ReportLab Docs:** https://www.reportlab.com/docs/
- **Vite Docs:** https://vitejs.dev/

---

<div align="center">
Happy coding! 🚀
</div>
