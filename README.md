git ## Eclari (Flask setup)

### Quickstart

1. Create a virtualenv and install deps:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the app:

```bash
python app.py
```

3. Open the site:

- Home: http://localhost:5000/
- Login: http://localhost:5000/login
- Student: http://localhost:5000/student
- Teacher: http://localhost:5000/teacher
- Finance: http://localhost:5000/finance
- Hall: http://localhost:5000/hall
- Coach: http://localhost:5000/coach
- Lab: http://localhost:5000/lab

### Notes
- HTML moved to `templates/` and assets to `static/`.
- Templates use `url_for` for static assets and internal links.
- `app.js` routes updated to Flask endpoints.

