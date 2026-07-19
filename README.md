# 🧳 AI Trip Planner (Flask version)

A plain HTML/CSS/JS frontend backed by a Flask API — no Streamlit. Same
trip-planning logic as before (AI itinerary, weather, budget, booking
links), but with full control over the UI.

Powered by the **Groq API** (free tier, no credit card required).

## Setup

### 1. Get a free Groq API key
Sign up at [console.groq.com/keys](https://console.groq.com/keys).

### 2. Install dependencies
```bash
cd ai-trip-planner-flask
pip install -r requirements.txt
```

### 3. Add your API key
```bash
cp .env.example .env
```
Edit `.env`:
```
GROQ_API_KEY=gsk_your-real-key-here
```

### 4. Run the app
```bash
python app.py
```
Open **http://localhost:5000** in your browser.

(This starts Flask's built-in dev server with `debug=True`, which
auto-reloads when you edit `app.py`, HTML, CSS, or JS.)

## Project structure

```
ai-trip-planner-flask/
├── app.py                  # Flask routes + API
├── requirements.txt
├── .env.example
├── templates/
│   └── index.html          # Page structure
├── static/
│   ├── style.css           # All styling (boarding-pass theme)
│   └── script.js           # Form handling, API calls, rendering
└── trip_planner/           # Same backend logic as the Streamlit version
    ├── llm.py               # Groq API client
    ├── itinerary.py         # Prompt building + itinerary generation
    ├── weather.py            # Open-Meteo geocoding + forecast
    ├── budget.py               # Cost-tier budget estimator (₹)
    └── booking_links.py        # Deep links to flight/hotel/activity search
```

## How it works

1. The browser loads `index.html`, which shows the trip-details form.
2. On submit, `script.js` sends a `POST /api/plan` request with the form
   data as JSON.
3. `app.py` calls the same `trip_planner` modules used in the Streamlit
   version (itinerary generation, weather, budget, booking links) and
   returns one JSON payload.
4. `script.js` renders that payload into the itinerary cards, weather
   grid, budget table, and booking link buttons — no page reload.

## Styling

All CSS lives in `static/style.css` — real, directly-authored CSS this
time (as opposed to overriding Streamlit's internal component classes),
so you can change colors, fonts, spacing, or layout freely without
fighting a framework. Look for the `:root` block at the top for the
color palette.

## Notes

- **Free tier limits** — Groq's free tier has generous but finite rate
  limits. Check current limits at
  [console.groq.com/settings/limits](https://console.groq.com/settings/limits).
- **Production use**: `debug=True` and Flask's built-in server are fine
  for local development but not for deploying publicly. For that, turn
  off debug mode and run behind a production WSGI server (e.g. gunicorn).
- **Booking links** are pre-filled search URLs, not live bookings.
- **Weather** is only reliable ~16 days out; further-future trips show
  the current outlook as a climate reference.

## Possible extensions

- Swap providers by editing `trip_planner/llm.py` (same `chat_json()`
  interface used elsewhere).
- Add client-side form validation feedback per field.
- Persist trips with a small SQLite database.
- Export itinerary to PDF.
