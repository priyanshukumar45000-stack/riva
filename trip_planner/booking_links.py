
from urllib.parse import quote_plus


def build_links(origin: str, destination: str, start_date: str, end_date: str, travelers: int) -> dict:
    dest_q = quote_plus(destination)
    origin_q = quote_plus(origin) if origin else ""

    links = {
        "flights_google": (
            f"https://www.google.com/travel/flights?q=Flights%20from%20{origin_q}"
            f"%20to%20{dest_q}%20on%20{start_date}%20through%20{end_date}"
        ),
        "flights_skyscanner": "https://www.skyscanner.com/transport/flights",
        "hotels_booking": (
            f"https://www.booking.com/searchresults.html?ss={dest_q}"
            f"&checkin={start_date}&checkout={end_date}&group_adults={travelers}"
        ),
        "hotels_airbnb": (
            f"https://www.airbnb.com/s/{dest_q}/homes"
            f"?checkin={start_date}&checkout={end_date}&adults={travelers}"
        ),
        "activities_viator": f"https://www.viator.com/searchResults/all?text={dest_q}",
        "activities_getyourguide": f"https://www.getyourguide.com/s/?q={dest_q}",
        "restaurants_tripadvisor": f"https://www.tripadvisor.com/Search?q={dest_q}%20restaurants",
    }
    return links


LINK_LABELS = {
    "flights_google": "✈️ Search flights (Google Flights)",
    "flights_skyscanner": "✈️ Search flights (Skyscanner)",
    "hotels_booking": "🏨 Search hotels (Booking.com)",
    "hotels_airbnb": "🏠 Search stays (Airbnb)",
    "activities_viator": "🎟️ Book activities (Viator)",
    "activities_getyourguide": "🎟️ Book activities (GetYourGuide)",
    "restaurants_tripadvisor": "🍽️ Find restaurants (TripAdvisor)",
}
