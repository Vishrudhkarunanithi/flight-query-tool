"""Running queries against the flight database."""


def run_query(db: list[dict], query: dict) -> dict:
    from datetime import datetime
    import math

    allowed_keys = {
        "flight_id",
        "origin",
        "destination",
        "departure_datetime",
        "arrival_datetime",
        "price",
        "min_price",
        "sort_by",
        "order",
        "limit"
    }

    if not isinstance(query, dict):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    if not set(query).issubset(allowed_keys):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    string_keys = {
        "flight_id",
        "origin",
        "destination"
    }

    for key in string_keys:
        if key in query and not isinstance(query[key], str):
            return {"query": query, "error": "INVALID_QUERY", "matches": []}

    datetime_keys = {
        "departure_datetime",
        "arrival_datetime"
    }

    for key in datetime_keys:
        if key in query:
            if not isinstance(query[key], str):
                return {"query": query, "error": "INVALID_QUERY", "matches": []}

            try:
                value = datetime.strptime(query[key], "%Y-%m-%d %H:%M")
                if value.strftime("%Y-%m-%d %H:%M") != query[key]:
                    raise ValueError
            except ValueError:
                return {"query": query, "error": "INVALID_QUERY", "matches": []}

    for key in ("price", "min_price"):
        if key in query:
            value = query[key]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                return {"query": query, "error": "INVALID_QUERY", "matches": []}
            if not math.isfinite(value) or value < 0:
                return {"query": query, "error": "INVALID_QUERY", "matches": []}

    if "sort_by" in query:
        if not isinstance(query["sort_by"], str) or query["sort_by"] not in  {
            "flight_id",
            "origin",
            "destination",
            "departure_datetime",
            "arrival_datetime",
            "price"
        }:
            return {"query": query, "error": "INVALID_QUERY", "matches": []}

    if "order" in query:
     if not isinstance(query["order"], str) or query["order"] not in ("asc", "desc") or "sort_by" not in query:
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    if "limit" in query:
        if isinstance(query["limit"], bool) or not isinstance(query["limit"], int):
            return {"query": query, "error": "INVALID_QUERY", "matches": []}
        if query["limit"] < 0:
            return {"query": query, "error": "INVALID_QUERY", "matches": []}

    matches = []

    for flight in db:
        matched = True

        for key in ("flight_id", "origin", "destination"):
            if key in query and flight[key] != query[key]:
                matched = False

        if "departure_datetime" in query:
            if flight["departure_datetime"] < query["departure_datetime"]:
                matched = False

        if "arrival_datetime" in query:
            if flight["arrival_datetime"] > query["arrival_datetime"]:
                matched = False

        if "price" in query:
            if flight["price"] > query["price"]:
                matched = False

        if "min_price" in query:
            if flight["price"] < query["min_price"]:
                matched = False

        if matched:
            matches.append(flight)

    if "sort_by" in query:
        key = query["sort_by"]
        reverse = query.get("order", "asc") == "desc"

        matches.sort(key=lambda flight: flight[key], reverse=reverse)

    if "limit" in query:
        matches = matches[:query["limit"]]

    return {
        "query": query,
        "matches": matches
    }


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    if isinstance(queries, dict):
        queries = [queries]

    if not isinstance(queries, list):
        return []

    return [run_query(db, query) for query in queries]