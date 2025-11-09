# 📁 Project Structure

This document explains the organization of the Eclari codebase.

```
Eclari/
├── 📄 Core Application Files
│   ├── app.py                      # Main Flask application (routes, PDF generation)
│   ├── supabase_client.py          # Database access layer (all queries)
│   └── requirements.txt            # Python dependencies
│
├── 🎨 Frontend Assets
│   ├── src/
│   │   ├── auth.js                 # Supabase authentication logic
│   │   └── app.js                  # Frontend application logic
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css          # Global styles
│   │   ├── images/                 # Role-specific background images
│   │   └── js/
│   │       ├── app.bundle.js       # Compiled frontend code
│   │       └── auth.bundle.js      # Compiled auth code
│   └── templates/
│       ├── login.html              # Login page
│       ├── index.html              # Landing page
│       ├── student.html            # Student dashboard
│       ├── subject.html            # Subject detail page
│       ├── teacher.html            # Teacher dashboard
│       ├── finance.html            # Finance dashboard
│       ├── hall.html               # Hall dashboard
│       ├── materials_dashboard.html # Lab/Sports dashboard
│       └── (other role dashboards)
│
├── 🗄️ Database Files
│   └── sql/
│       ├── database_migration_year_groups_SAFE.sql  # Main schema + data
│       ├── rls_policies_books.sql                   # Book access policies
│       ├── rls_policies_materials.sql               # Material access policies
│       └── rls_policies_storage.sql                 # File storage policies
│
├── 📚 Documentation
│   └── docs/
│       ├── DATABASE_SCHEMA.md      # Database table structure
│       ├── IMPLEMENTATION_COMPLETE.md  # Feature completion notes
│       ├── DEVELOPMENT.md          # Development guide (this is comprehensive!)
│       └── API.md                  # API endpoint documentation
│
├── ⚙️ Configuration
│   ├── .env                        # Environment variables (not in git)
│   ├── .env.example                # Template for .env file
│   ├── .gitignore                  # Files to exclude from git
│   ├── package.json                # Node.js dependencies (for Vite)
│   ├── vite.config.js              # Vite bundler configuration
│   └── setup-dev.sh                # Development setup script
│
└── 🔧 Build Artifacts (generated)
    ├── .venv/                      # Python virtual environment
    ├── node_modules/               # Node.js packages
    ├── __pycache__/                # Python bytecode cache
    └── static/js/*.bundle.js       # Compiled JavaScript
```

---

## Key Files Explained

### Backend (Python)

**`app.py`** - The heart of the application
- Flask web server configuration
- Route definitions (`/login`, `/dashboard/<role>`, `/subject/<id>`)
- API endpoints (`/api/upload-proof`, `/api/generate-clearance-pdf`)
- JWT token verification decorator
- PDF generation with ReportLab
- Session management

**`supabase_client.py`** - Database abstraction layer
- Supabase client initialization
- Student data functions (`get_student_by_id`, `get_student_books`)
- Teacher data functions (`get_teacher_classes`, `get_pending_approvals`)
- Finance/Hall/Lab data functions
- Clearance calculation logic
- File upload handling
- Error handling and logging

---

### Frontend (JavaScript)

**`src/auth.js`** - Authentication module
- Supabase auth client setup
- Login/logout functions
- Session management (cookies)
- Auth state change listeners
- Role detection from user metadata

**`src/app.js`** - Application logic
- Role-specific visual effects (login page)
- Form submission handlers
- Dashboard interactivity
- File upload with progress
- Real-time updates

**Build Process:**
```bash
npm run build  # Compiles src/*.js → static/js/*.bundle.js
```

---

### Templates (Jinja2 + HTML)

**`templates/login.html`**
- Beautiful role-specific design
- Background changes based on selected role
- Client-side form validation
- Supabase authentication integration

**`templates/student.html`**
- Overall clearance percentage display
- Subject portals with individual percentages
- Y1: Photo upload interface
- Y2: Physical return tracking
- PDF download button (100% only)

**`templates/subject.html`**
- Subject-specific clearance details
- Book list with return status
- Material list with return status
- Upload interface for Y1 students
- Teacher approval status

**`templates/teacher.html`**
- Classes taught overview
- Pending approvals section (Y1 photos)
- Student return tracking
- Bulk approval actions

**Role-specific dashboards:**
- `finance.html` - Outstanding balances, replacement costs
- `hall.html` - Room clearance status
- `materials_dashboard.html` - Lab equipment, sports gear

---

### Database (SQL)

**`sql/database_migration_year_groups_SAFE.sql`**
- Complete schema definition
- All 12 tables with relationships
- Sample data for testing
- Year group (Y1/Y2) support
- Clearance tracking fields

**RLS Policy Files:**
- `rls_policies_books.sql` - Students can only see their books
- `rls_policies_materials.sql` - Students can only see their materials
- `rls_policies_storage.sql` - Photo access controls

---

### Configuration

**`.env` (not in git)**
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=service_role_key_here
SUPABASE_ANON_KEY=anon_key_here
FLASK_SECRET_KEY=random_secret_here
PDF_OWNER_PASSWORD=secure_password
```

**`.env.example` (template)**
- Copy this to `.env` and fill in your values
- Tracked in git as a reference

**`.gitignore`**
- Excludes sensitive files (`.env`, `*.key`)
- Excludes build artifacts (`node_modules/`, `.venv/`)
- Excludes temporary files (`*_FIX.md`, `test_*.py`)
- Excludes media files (`*.mp4`, `*.tmp`)

---

## Data Flow

### Student Uploads Photo (Y1 Workflow)

```
1. Student clicks "Upload Photo" on subject.html
   ↓
2. JavaScript in subject.html calls /api/upload-proof
   ↓
3. Flask (app.py) receives file and metadata
   ↓
4. supabase_client.py uploads to Storage bucket
   ↓
5. Database updated with proof_image_url
   ↓
6. Teacher sees pending approval in teacher.html
   ↓
7. Teacher clicks "Approve"
   ↓
8. /api/approve-proof marks book as returned
   ↓
9. Student's clearance % increases
```

### Student Returns Book Physically (Y2 Workflow)

```
1. Y2 student brings book to teacher
   ↓
2. Teacher marks as returned in teacher.html
   ↓
3. /api/mark-returned updates database
   ↓
4. Student sees "Returned" status in student.html
   ↓
5. Student's clearance % increases
```

### Student Downloads Clearance Certificate

```
1. Student reaches 100% clearance
   ↓
2. "Download Certificate" button appears
   ↓
3. Clicks button → /api/generate-clearance-pdf
   ↓
4. Flask generates PDF with ReportLab
   ↓
5. Browser downloads "Clearance_Certificate_ST001.pdf"
```

---

## Build and Deployment

### Development

```bash
# Backend (Flask)
source .venv/bin/activate
flask run --debug

# Frontend (Vite watch mode)
npm run dev
```

### Production

```bash
# Build frontend assets
npm run build

# Run with production server
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```

---

## Adding New Features

### Example: Add a "Lab Dashboard"

1. **Database:** Create `lab_staff` table in SQL migration
2. **Python:** Add `get_lab_by_id()` in `supabase_client.py`
3. **Route:** Add `/dashboard/lab` route in `app.py`
4. **Template:** Create `templates/lab.html`
5. **Auth:** Add 'lab' role to login dropdown in `login.html`

See [`docs/DEVELOPMENT.md`](./docs/DEVELOPMENT.md) for detailed examples.

---

## Common Tasks

### Update Styles
Edit `static/css/styles.css` and refresh browser.

### Update Frontend Logic
Edit `src/app.js`, run `npm run build`, refresh browser.

### Add New Route
Add to `app.py`:
```python
@app.route("/new-page")
@verify_supabase_token
def new_page():
    return render_template("new_page.html")
```

### Add New Database Query
Add to `supabase_client.py`:
```python
def get_something(id):
    result = supabase.table('table_name').select('*').eq('id', id).execute()
    return result.data
```

---

## File Size Reference

- **Small** (< 500 lines): Most templates, CSS, config files
- **Medium** (500-1000 lines): `app.py`, `supabase_client.py`, `app.js`
- **Large** (> 1000 lines): Database migration SQL (1000+ lines with sample data)

---

## Dependencies

### Python (`requirements.txt`)
- `flask` - Web framework
- `python-dotenv` - Environment variable loading
- `supabase` - Database client
- `reportlab` - PDF generation

### Node.js (`package.json`)
- `@supabase/supabase-js` - Frontend auth
- `vite` - Module bundler

---

## Security Notes

🔒 **Never commit:**
- `.env` file (contains secrets)
- Service role keys (only use in backend)
- User passwords or tokens

✅ **Safe to commit:**
- `.env.example` (template only)
- Anonymous keys (safe for frontend)
- Public URLs

🛡️ **RLS Policies protect:**
- Students can't see other students' data
- Teachers can only see their classes
- File uploads are scoped to authenticated users

---

## Troubleshooting

**"Module not found"**
- Run `pip install -r requirements.txt`
- Make sure `.venv` is activated

**"Invalid token"**
- Clear cookies and login again
- Check `.env` has correct Supabase URL/keys

**Frontend changes not showing**
- Run `npm run build` after editing `src/*.js`
- Hard refresh browser (Ctrl+Shift+R)

**Database errors**
- Check Supabase project is active
- Verify RLS policies are applied
- Check table exists in SQL editor

---

For more details, see:
- [Development Guide](./docs/DEVELOPMENT.md)
- [API Documentation](./docs/API.md)
- [Database Schema](./docs/DATABASE_SCHEMA.md)
