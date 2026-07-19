
from . import llm

SYSTEM_PROMPT = """You are an expert travel planner. You design realistic, \
well-paced itineraries tailored to the traveler's interests, budget tier, \
and trip length. You always respond with ONLY a single valid JSON object \
matching the exact schema you are given -- no prose, no markdown fences, \
no commentary.
"""

JSON_SCHEMA_HINT = """
Respond with a JSON object of this exact shape:

{
  "destination_summary": "2-3 sentence overview of the destination and why it fits the traveler",
  "days": [
    {
      "day": 1,
      "title": "short theme for the day, e.g. 'Old Town & Harbor'",
      "morning": "activity description",
      "afternoon": "activity description",
      "evening": "activity description",
      "meal_suggestions": ["restaurant or food area suggestion", "..."],
      "notes": "practical tip for the day (transport, booking ahead, etc.)"
    }
  ],
  "packing_tips": ["tip 1", "tip 2", "tip 3"],
  "local_tips": ["cultural note or etiquette tip", "..."]
}

The "days" array must have exactly the number of days requested. Keep each
field concise (1-2 sentences). Tailor activities specifically to the stated
interests, not generic tourist filler.
"""


def build_user_prompt(
    destination: str,
    start_date: str,
    end_date: str,
    num_days: int,
    travelers: int,
    budget_tier: str,
    interests: list[str],
    pace: str,
) -> str:
    interests_str = ", ".join(interests) if interests else "general sightseeing"
    return f"""Plan a trip with these details:
- Destination: {destination}
- Dates: {start_date} to {end_date} ({num_days} days)
- Travelers: {travelers}
- Budget tier: {budget_tier}
- Interests: {interests_str}
- Preferred pace: {pace}

{JSON_SCHEMA_HINT}
"""


def generate_itinerary(
    destination: str,
    start_date: str,
    end_date: str,
    num_days: int,
    travelers: int,
    budget_tier: str,
    interests: list[str],
    pace: str,
    model: str = llm.DEFAULT_MODEL,
) -> dict:
    prompt = build_user_prompt(
        destination, start_date, end_date, num_days, travelers,
        budget_tier, interests, pace,
    )
    data = llm.chat_json(SYSTEM_PROMPT, prompt, model=model)
    return _normalize(data, num_days)


def _normalize(data: dict, num_days: int) -> dict:
    """Guard against a model that returns fewer/extra days or missing keys."""
    days = data.get("days", [])[:num_days]

    while len(days) < num_days:
        idx = len(days) + 1
        days.append({
            "day": idx,
            "title": f"Day {idx}",
            "morning": "Free time to explore -- the AI didn't fill this in, add your own plan.",
            "afternoon": "",
            "evening": "",
            "meal_suggestions": [],
            "notes": "",
        })

    for i, d in enumerate(days, start=1):
        d.setdefault("day", i)
        d.setdefault("title", f"Day {i}")
        for key in ("morning", "afternoon", "evening", "notes"):
            d.setdefault(key, "")
        d.setdefault("meal_suggestions", [])

    data["days"] = days
    data.setdefault("destination_summary", "")
    data.setdefault("packing_tips", [])
    data.setdefault("local_tips", [])
    return data
