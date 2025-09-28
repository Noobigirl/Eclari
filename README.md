

# Eclari - Student Clearance Portal

A Flask-based web application for African Leadership Academy's student clearance system with Supabase authentication.

## 🚀 Features

- **Supabase Authentication**: Secure login/logout with JWT verification
- **Role-based Dashboards**: Different interfaces for students, teachers, finance, hall staff, coaches, and lab managers
- **Modern Frontend**: Vite-bundled JavaScript with ES6 modules
- **Responsive Design**: Works on desktop and mobile devices

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Database & Auth**: Supabase
- **Frontend**: Vanilla JavaScript, Vite bundler
- **Styling**: Custom CSS

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- Supabase account and project

## 🔧 Quick Setup

### Option 1: Automated Setup (Recommended)

```bash
# Run the setup script
./setup-dev.sh
```

### Option 2: Manual Setup

1. **Clone and enter directory**
   ```bash
   git clone <repository-url>
   cd Eclari
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase credentials
   ```

3. **Install Python dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Install Node.js dependencies**
   ```bash
   npm install
   ```

5. **Build frontend assets**
   ```bash
   npm run build
   ```

## 🌐 Supabase Configuration

1. Create a new Supabase project at [supabase.com](https://supabase.com)

2. Set up your user table with roles:
   ```sql
   -- Users will be automatically created in auth.users
   -- Make sure to add role information in raw_user_meta_data when creating users
   -- Example: {"role": "student"} or {"role": "teacher"}
   ```

3. Configure Row Level Security (RLS) as needed

4. Get your credentials from Settings > API:
   - Project URL
   - `anon` public key (for frontend)
   - `service_role` key (for backend)

## 🏃‍♂️ Running the Application

### Development Mode

1. **Start the Flask server**
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   python app.py
   ```

2. **For frontend development (optional)**
   ```bash
   # In another terminal for auto-rebuild on changes
   npm run dev
   ```

3. **Visit the app**
   Open http://localhost:5000

### Production Build

```bash
npm run build
python app.py
```

## 🔐 Authentication Flow

1. **User Login**: Users enter ALA email and password on `/login`
2. **Supabase Auth**: JavaScript calls Supabase to authenticate
3. **Session Storage**: JWT token stored in cookies for Flask
4. **Route Protection**: Flask verifies tokens on protected routes
5. **Role-based Redirect**: Users redirected to appropriate dashboard

### Supported Roles

- `student` → Student clearance portal
- `teacher` → Teacher validation dashboard
- `finance` → Financial clearance management
- `hall` → Hall inspection dashboard
- `coach` → Sports equipment tracking
- `lab` → Laboratory equipment management

## 📁 Project Structure

```
Eclari/
├── app.py              # Flask application with auth
├── supabase_client.py  # Supabase configuration
├── requirements.txt    # Python dependencies
├── package.json        # Node.js dependencies
├── vite.config.js      # Vite bundler config
├── src/                # JavaScript source files
│   ├── auth.js         # Supabase auth functions
│   └── app.js          # Main application logic
├── static/             # Static assets
│   ├── css/
│   ├── images/
│   └── js/             # Built JavaScript bundles
├── templates/          # Flask templates
│   ├── login.html
│   ├── student.html
│   ├── teacher.html
│   └── ...
└── setup-dev.sh        # Development setup script
```

## 🔧 Development Commands

```bash
# Install dependencies
npm install
pip install -r requirements.txt

# Build JavaScript for production
npm run build

# Build JavaScript with watch mode (development)
npm run dev

# Run Flask development server
python app.py

# Set up development environment
./setup-dev.sh
```

## 🚪 API Endpoints

- `GET /` - Home page
- `GET /login` - Login page
- `GET /dashboard/<role>` - Role-based dashboards
- `GET /logout` - Logout and clear session
- `GET /subject` - Subject detail page (protected)

## 🛡️ Security Features

- JWT token verification on all protected routes
- Role-based access control
- Secure cookie handling
- Supabase Row Level Security integration
- Session management and cleanup

## 🐛 Troubleshooting

### Common Issues

1. **"supabase-token cookie not found"**
   - User needs to log in through the login page
   - Check that Supabase credentials are correct

2. **"Invalid token" errors**
   - Token may have expired
   - Clear browser cookies and log in again

3. **Build failures**
   - Run `npm install` to ensure all dependencies are installed
   - Check Node.js version (requires 16+)

4. **Role access denied**
   - Verify user role is set correctly in Supabase user metadata
   - Check that role matches the dashboard being accessed

### Environment Variables

Make sure these are set in your `.env` file:

```env
FLASK_SECRET_KEY=your-secure-secret-key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
SUPABASE_ANON_KEY=your-anon-public-key
```

## 📝 Notes

- The application uses email format `{ala-id}@ala.edu` for authentication
- User roles must be stored in Supabase `raw_user_meta_data`
- Frontend assets are bundled with Vite for optimal performance
- All dashboard pages require authentication

roles for loged in users:
student
teacher
finance
hall
coach
lab

