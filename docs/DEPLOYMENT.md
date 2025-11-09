# 🚀 Deployment Guide

Complete guide for deploying Eclari to production.

---

## Table of Contents

1. [Render Deployment](#render-deployment)
2. [Environment Variables](#environment-variables)
3. [Troubleshooting](#troubleshooting)
4. [Post-Deployment Setup](#post-deployment-setup)
5. [Alternative Platforms](#alternative-platforms)

---

## Render Deployment

### Prerequisites

- GitHub account
- Render account (free tier works!)
- Supabase project set up
- Code pushed to GitHub

### Step-by-Step

**1. Prepare Your Repository**

```bash
# Make sure all changes are committed
git add .
git commit -m "Prepare for deployment"
git push origin main
```

**2. Create Web Service on Render**

1. Go to https://dashboard.render.com/
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account (if not already)
4. Select the `Eclari` repository
5. Render will auto-detect Python

**3. Configure Build Settings**

Render should auto-detect from `render.yaml`, but verify:

- **Name:** `eclari` (or your choice)
- **Environment:** `Python`
- **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt && npm install && npm run build`
- **Start Command:** `gunicorn --bind 0.0.0.0:$PORT --workers 4 app:app`
- **Python Version:** `3.13.9` (from `runtime.txt`)

**4. Set Environment Variables**

Click **"Environment"** tab and add:

| Key | Value | Notes |
|-----|-------|-------|
| `SUPABASE_URL` | `https://xxx.supabase.co` | From Supabase project settings |
| `SUPABASE_KEY` | `eyJhbG...` | Service role key (keep secret!) |
| `SUPABASE_ANON_KEY` | `eyJhbG...` | Anonymous key (safe for frontend) |
| `FLASK_SECRET_KEY` | Generate with command below | Used for session encryption |
| `FLASK_ENV` | `production` | Sets production mode |
| `PDF_OWNER_PASSWORD` | Your choice | PDF encryption password |

**Generate Flask Secret Key:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**5. Deploy!**

- Click **"Create Web Service"**
- Wait for build to complete (~5 minutes)
- Your app will be live at `https://eclari.onrender.com` (or your chosen name)

---

## Environment Variables

### Required Variables

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_role_key_here
SUPABASE_ANON_KEY=your_anon_key_here

# Flask Configuration
FLASK_SECRET_KEY=generate_with_secrets_module
FLASK_ENV=production

# PDF Configuration
PDF_OWNER_PASSWORD=secure_password_here
```

### Where to Find Supabase Keys

1. Go to your Supabase project dashboard
2. Click **"Settings"** (gear icon in sidebar)
3. Click **"API"**
4. Copy:
   - **Project URL** → `SUPABASE_URL`
   - **anon/public key** → `SUPABASE_ANON_KEY`
   - **service_role key** → `SUPABASE_KEY` ⚠️ Keep this secret!

### Security Notes

- ✅ `SUPABASE_ANON_KEY` - Safe to expose in frontend
- ⚠️ `SUPABASE_KEY` - Service role key, **NEVER expose** to frontend
- ⚠️ `FLASK_SECRET_KEY` - Keep secret, used for session security

---

## Troubleshooting

### Common Issues

#### 1. "ModuleNotFoundError: No module named 'supabase_auth.http_clients'"

**Cause:** Version incompatibility with supabase package

**Solution:** The project uses `supabase==2.11.0` (a stable LTS version) to avoid dependency conflicts. Ensure your `requirements.txt` has:
```
supabase==2.11.0
```

**NOT** version 2.20.0 or newer, which has breaking changes with the auth modules.

Then redeploy with "Clear build cache & deploy" in Render.

---

#### 2. Build Fails with "npm command not found"

**Cause:** Node.js not available in build environment

**Solution:** Update `render.yaml`:
```yaml
buildCommand: "pip install -r requirements.txt && npm install && npm run build"
```

Or set build command in Render dashboard to skip npm:
```bash
pip install --upgrade pip && pip install -r requirements.txt
```

(Frontend assets are pre-built in repository)

---

#### 3. "Invalid Supabase credentials"

**Cause:** Wrong environment variables

**Solution:**
1. Double-check environment variables in Render dashboard
2. Verify keys match your Supabase project
3. Ensure no extra spaces in keys
4. Check Supabase project is active

---

#### 4. 500 Error on Login

**Cause:** Missing or incorrect `FLASK_SECRET_KEY`

**Solution:**
```bash
# Generate new secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Add to Render environment variables
FLASK_SECRET_KEY=<generated_key>
```

Then click **"Manual Deploy"** → **"Clear build cache & deploy"**

---

#### 5. Database Connection Fails

**Cause:** RLS policies not applied or wrong permissions

**Solution:**
1. Go to Supabase SQL Editor
2. Run all migration files in `sql/` folder:
   - `database_migration_year_groups_SAFE.sql`
   - `rls_policies_books.sql`
   - `rls_policies_materials.sql`
   - `rls_policies_storage.sql`
3. Verify tables exist in Table Editor
4. Test RLS policies with sample data

---

#### 6. Static Files Not Loading

**Cause:** Frontend not built or CORS issues

**Solution:**
```bash
# Locally rebuild frontend
npm run build

# Commit and push
git add static/js/
git commit -m "Rebuild frontend assets"
git push origin main
```

Render will auto-deploy on push.

---

#### 7. Upload Fails / "Storage bucket not found"

**Cause:** Supabase Storage bucket not created

**Solution:**
1. Go to Supabase Dashboard → **Storage**
2. Click **"New bucket"**
3. Name: `clearance-proofs`
4. **Public bucket:** Yes (or set custom policies)
5. Apply RLS policies from `sql/rls_policies_storage.sql`

---

### Viewing Logs

**On Render:**
1. Go to your web service
2. Click **"Logs"** tab
3. View real-time logs

**Common log messages:**
```bash
# Good signs:
[INFO] Booting worker with pid: 123
[INFO] Starting gunicorn 23.0.0
[INFO] Listening at: http://0.0.0.0:10000

# Bad signs:
ModuleNotFoundError: No module named 'X'
ImportError: cannot import name 'X'
Exception: Invalid Supabase credentials
```

---

## Post-Deployment Setup

### 1. Test Core Functionality

- [ ] Visit your deployed URL
- [ ] Test login with sample credentials
- [ ] Check student dashboard loads
- [ ] Test image upload (Y1 student)
- [ ] Test approval workflow (teacher)
- [ ] Generate PDF certificate (100% cleared student)

### 2. Configure Custom Domain (Optional)

**On Render:**
1. Go to your web service → **"Settings"**
2. Click **"Custom Domains"**
3. Add your domain (e.g., `eclari.yourschool.com`)
4. Follow DNS configuration instructions
5. Render provides free SSL certificate

### 3. Set Up Monitoring

**Render Built-in:**
- Auto-restart on crashes
- Health checks
- Email alerts

**External (Optional):**
- [UptimeRobot](https://uptimerobot.com/) - Free uptime monitoring
- [Sentry](https://sentry.io/) - Error tracking
- [LogRocket](https://logrocket.com/) - Session replay

### 4. Database Backup

**Supabase automatic backups:**
- Free plan: Daily backups (7 days retention)
- Pro plan: Point-in-time recovery

**Manual backup:**
```bash
# Export database to SQL file
# (Use Supabase dashboard → Database → Export)
```

---

## Alternative Platforms

### Heroku

```bash
# Install Heroku CLI
heroku login

# Create app
heroku create eclari

# Set buildpacks
heroku buildpacks:add heroku/python
heroku buildpacks:add heroku/nodejs

# Set environment variables
heroku config:set SUPABASE_URL=xxx
heroku config:set SUPABASE_KEY=xxx
heroku config:set FLASK_SECRET_KEY=xxx

# Deploy
git push heroku main
```

**Add `Procfile`:**
```
web: gunicorn --bind 0.0.0.0:$PORT --workers 4 app:app
```

---

### Railway

1. Go to https://railway.app/
2. Click **"New Project"** → **"Deploy from GitHub"**
3. Select `Eclari` repository
4. Set environment variables in **"Variables"** tab
5. Railway auto-detects Python and deploys

**Add `railway.json` (optional):**
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn --bind 0.0.0.0:$PORT --workers 4 app:app",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

---

### DigitalOcean App Platform

1. Go to https://cloud.digitalocean.com/apps
2. Click **"Create App"**
3. Connect GitHub repository
4. Configure:
   - **Resource Type:** Web Service
   - **Build Command:** `pip install -r requirements.txt && npm install && npm run build`
   - **Run Command:** `gunicorn --bind 0.0.0.0:8080 --workers 4 app:app`
5. Add environment variables
6. Deploy

---

## Performance Optimization

### For Production

**1. Enable Gunicorn Workers**

```bash
# In render.yaml or start command
gunicorn --bind 0.0.0.0:$PORT --workers 4 --threads 2 app:app
```

- **Workers:** 2-4 per CPU core
- **Threads:** 2-4 per worker

**2. Add Caching**

Install Redis:
```bash
pip install redis flask-caching
```

Configure:
```python
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.getenv('REDIS_URL')
})

@cache.cached(timeout=300)
def get_student_data(student_id):
    # Expensive database query
    pass
```

**3. CDN for Static Assets**

Use Cloudflare or similar:
- Free tier available
- Caches `static/*` files
- Reduces server load

---

## Security Checklist

Before going live:

- [ ] All secrets in environment variables (not in code)
- [ ] `FLASK_ENV=production` set
- [ ] `FLASK_SECRET_KEY` is strong and unique
- [ ] RLS policies applied to all tables
- [ ] Storage bucket has proper access policies
- [ ] HTTPS enabled (Render does this automatically)
- [ ] CORS configured correctly
- [ ] File upload size limits enforced
- [ ] Rate limiting considered (optional)

---

## Maintenance

### Regular Tasks

**Weekly:**
- Check error logs
- Monitor uptime
- Review Supabase usage

**Monthly:**
- Update dependencies: `pip list --outdated`
- Review database performance
- Check storage usage

**As Needed:**
- Deploy new features
- Fix reported bugs
- Update documentation

---

## Support

**Deployment Issues:**
- Check [Render Status](https://status.render.com/)
- Check [Supabase Status](https://status.supabase.com/)
- Review logs in Render dashboard

**Code Issues:**
- Check [GitHub Issues](https://github.com/Noobigirl/Eclari/issues)
- Review [DEVELOPMENT.md](./DEVELOPMENT.md)
- Check [API.md](./API.md)

---

<div align="center">

**Happy Deploying! 🚀**

Questions? Open an issue on GitHub.

</div>
