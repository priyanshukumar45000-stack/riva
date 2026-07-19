import datetime as dt

from flask import Flask, jsonify, render_template, request

from trip_planner import llm, weather, budget as budget_mod, booking_links, itinerary

app = Flask(__name__)


@app.route("/")
def index():
    return render_template(
        "index.html",
        models=llm.AVAILABLE_MODELS,
        default_model=llm.DEFAULT_MODEL,
    )


@app.route("/api/status")
def status():
    """Frontend checks this on load to know whether to show the API-key warning."""
    return jsonify({"configured": llm.is_configured()})


@app.route("/api/plan", methods=["POST"])
def plan():
    data = request.get_json(silent=True) or {}

    destination = (data.get("destination") or "").strip()
    origin = (data.get("origin") or "").strip()
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    travelers = data.get("travelers", 1)
    budget_tier = data.get("budget_tier", "mid-range")
    interests = data.get("interests", [])
    pace = data.get("pace", "balanced")
    model = data.get("model") or llm.DEFAULT_MODEL

    if not destination:
        return jsonify({"error": "Destination is required."}), 400
    if not start_date or not end_date:
        return jsonify({"error": "Start and end dates are required."}), 400

    try:
        sd = dt.date.fromisoformat(start_date)
        ed = dt.date.fromisoformat(end_date)
    except ValueError:
        return jsonify({"error": "Dates must be in YYYY-MM-DD format."}), 400

    num_days = (ed - sd).days + 1
    if num_days < 1:
        return jsonify({"error": "End date must be on or after start date."}), 400
    if num_days > 30:
        return jsonify({"error": "Trips longer than 30 days aren't supported yet."}), 400

    try:
        travelers = max(1, int(travelers))
    except (TypeError, ValueError):
        travelers = 1

    try:
        itin = itinerary.generate_itinerary(
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            num_days=num_days,
            travelers=travelers,
            budget_tier=budget_tier,
            interests=interests,
            pace=pace,
            model=model,
        )
    except llm.LLMError as e:
        return jsonify({"error": str(e)}), 502

    # Weather
    forecast = []
    geo = weather.geocode(destination)
    if geo:
        raw_forecast = weather.get_forecast(geo["latitude"], geo["longitude"], days=min(num_days, 16))
        for f in raw_forecast:
            forecast.append({**f, "description": weather.describe_code(f["code"])})

    # Budget
    b = budget_mod.estimate_budget(num_days, travelers, budget_tier)
    budget_payload = {
        "total": budget_mod.format_inr(b["grand_total"]),
        "table": budget_mod.format_budget_table(b),
    }

    # Booking links
    links = booking_links.build_links(origin, destination, start_date, end_date, travelers)
    link_items = [
        {"key": k, "label": booking_links.LINK_LABELS.get(k, k), "url": v}
        for k, v in links.items()
    ]

    return jsonify({
        "itinerary": itin,
        "weather": forecast,
        "budget": budget_payload,
        "links": link_items,
        "meta": {"destination": destination, "num_days": num_days},
    })


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
