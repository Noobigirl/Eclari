

### Quickstart

How to run Eclari
1. Create a virtualenv and install deps:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the app in the terminal:

```bash
python app.py
```


### Notes
- HTML moved to `templates/` and assets to `static/`.
- Templates use `url_for` for static assets and internal links.
- `app.js` routes updated to Flask endpoints.

