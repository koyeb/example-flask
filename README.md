# Pirenily — A Personal Archive

Pirenily is my personal portfolio site: a place to show off design work, side projects, and the odd creative experiment, all in one archive. Live at [pirenily.com](https://pirenily.com).

## Features

- **Design** — collaborative club work and commissioned pieces in one gallery.
- **Play** — personal, non-commissioned projects.
- **Projects** — coding and UI/UX work, filterable by a Code / UI-UX toggle, sorted newest first.
- **About** — bio, self-photography, and contact links 

## Tech Stack

- **Backend:** Flask (Python), Jinja2 templates
- **Frontend:** HTML, CSS, vanilla JavaScript
- **Fonts:** Google Fonts
- **Hosting:** Koyeb

## Getting Started

Requirements: Python 3.8+, pip, a modern browser.

```bash
git clone https://github.com/tuechile/example-flask.git
cd example-flask
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
flask run
```

Then open `http://127.0.0.1:5000` in your browser.

## Deployment

Deployed on [Koyeb](https://www.koyeb.com), following their [Flask deployment guide](https://github.com/koyeb/example-flask). The Koyeb web service is linked directly to this GitHub repo (which includes the `Procfile` and `requirements.txt` it needs), and a custom domain points at the service Koyeb provides. Pushing to `main` triggers a redeploy automatically.

## Project Structure

```
example-flask/
├── app.py                     # Flask app and routes
├── requirements.txt
├── Procfile
├── design.md                  # Design notes
├── templates/
│   ├── layout.html            # Shared nav/footer base template
│   ├── index.html             # Homepage (landing + Projects section)
│   ├── about.html
│   ├── collab.html            # "Design" page (clubs + commissions)
│   ├── personal.html          # "Play" page
│   ├── collab websites/       # Sub-pages linked from Design
│   ├── Project/               # Sub-pages linked from Projects
│   └── personal websites/     # Sub-pages linked from Play
└── static/
    ├── css/                   # styles.css, body.css, ux.css
    ├── loading.js / clickimage.js
    └── asset/
        ├── fonts/
        └── images/
```
