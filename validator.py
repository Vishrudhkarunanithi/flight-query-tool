"""Row validation: airport list loading, single-row checks, record building."""


def load_airports(path: str) -> set[str]:
   airports = set()

   with open(path, "r", encoding="utf-8") as file:
        for line in file:
            code = line.strip()

            if code and not code.startswith("#"):
                airports.add(code)

   return airports

def validate_row(fields: list[str], airports: set[str]) -> str | None:
    import re
    import math
    from datetime import datetime

    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"

    fields = [field.strip() for field in fields]

    if any(field == "" for field in fields):
        return "MISSING_FIELD"

    flight_id, origin, destination, departure, arrival, price = fields

    if not re.fullmatch(r"[A-Za-z0-9]{2,8}", flight_id):
        return "INVALID_FLIGHT_ID"

    if not re.fullmatch(r"[A-Z]{3}", origin) or origin not in airports:
        return "INVALID_ORIGIN"

    if not re.fullmatch(r"[A-Z]{3}", destination) or destination not in airports:
        return "INVALID_DESTINATION"

    if origin == destination:
        return "SAME_ORIGIN_DESTINATION"

    def valid_datetime(value):
        try:
            parsed = datetime.strptime(value, "%Y-%m-%d %H:%M")
            return parsed.strftime("%Y-%m-%d %H:%M") == value
        except ValueError:
            return False

    if not valid_datetime(departure):
        return "INVALID_DEPARTURE"

    if not valid_datetime(arrival):
        return "INVALID_ARRIVAL"

    departure_dt = datetime.strptime(departure, "%Y-%m-%d %H:%M")
    arrival_dt = datetime.strptime(arrival, "%Y-%m-%d %H:%M")

    if arrival_dt <= departure_dt:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"

    try:
        price_value = float(price)
        if not math.isfinite(price_value):
            return "INVALID_PRICE"
    except ValueError:
        return "INVALID_PRICE"

    if price_value <= 0:
        return "NON_POSITIVE_PRICE"

    return None


def to_record(fields: list[str]) -> dict:
    fields = [field.strip() for field in fields]

    return {
        "flight_id": fields[0],
        "origin": fields[1],
        "destination": fields[2],
        "departure_datetime": fields[3],
        "arrival_datetime": fields[4],
        "price": float(fields[5])
    }