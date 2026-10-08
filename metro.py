import os

import httpx
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("metro")

FARE_BASE = "https://lankametro.lk/metrobus-proxy/fare-service/api/v1"
PLAN_URL = f"{FARE_BASE}/journeys/plan"
STOPS_SEARCH_URL = f"{FARE_BASE}/stops/search"
# ponytail: token from env only. Set METRO_JWT in Vercel (and your shell for local
# dev). Expires 2027-03-27 — re-grab from the site and update the env var when it lapses.
JWT = os.environ.get("METRO_JWT", "")


@mcp.tool()
async def plan_journey(
    from_stop_id: str,
    to_stop_id: str,
    date: str | None = None,
    now: bool = False,
) -> dict:
    """Plan bus journeys between two Lanka Metro stops.

    from_stop_id / to_stop_id: stop UUIDs.
    date: YYYY-MM-DD for a full day's options (defaults to today if omitted and now is False).
    now: if True, only departures still upcoming from the current moment.
    """
    params = {"from_stop_id": from_stop_id, "to_stop_id": to_stop_id}
    if now:
        params["now"] = "true"
    elif date:
        params["date"] = date

    async with httpx.AsyncClient() as client:
        r = await client.get(
            PLAN_URL,
            params=params,
            headers={"Authorization": f"Bearer {JWT}"},
            timeout=20,
        )
    if r.status_code != 200:
        return {"error": r.status_code, "body": r.text}
    return r.json().get("data", {})


@mcp.tool()
async def search_stops(q: str) -> list[dict]:
    """Search Lanka Metro stops by name (substring match, tri-lingual).

    Returns matching stops with id, stop_code, names and coordinates. Results
    can include duplicates (same place, different code/direction), so let the
    caller pick the right id.
    """
    headers = {"Authorization": f"Bearer {JWT}"}
    term = q.strip()
    async with httpx.AsyncClient() as client:
        while len(term) >= 3:
            r = await client.get(
                STOPS_SEARCH_URL, params={"q": term}, headers=headers, timeout=20
            )
            if r.status_code != 200:
                return [{"error": r.status_code, "body": r.text}]
            stops = r.json().get("data", {}).get("stops", [])
            if stops:
                return stops
            term = term[:-1]
    return []


if __name__ == "__main__":
    # ponytail: stdio for local dev, streamable-http when PORT is set (any cloud host).
    if port := os.environ.get("PORT"):
        mcp.run(transport="streamable-http", host="0.0.0.0", port=int(port), stateless_http=True)
    else:
        mcp.run(transport="stdio")
