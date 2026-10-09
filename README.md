# Metro MCP

An MCP server for **Lanka Metro** bus travel. It runs locally and gives Claude two tools:

- `search_stops(q)` — find bus stops by name (returns id, code, names, coordinates)
- `plan_journey(from_stop_id, to_stop_id, date?, now?)` — journey options between two stops

It runs **on your own machine** over stdio, so Lanka Metro sees requests from your normal
connection. (It is not hosted — cloud/datacenter IPs get blocked by the upstream API.)

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

## Setup

```bash
git clone https://github.com/MusthafaAltaf2001/metro-mcp.git
cd metro-mcp
uv sync
```

### Get a token

The server authenticates with a JWT the Lanka Metro web app uses. Grab it once:

1. Open https://lankametro.lk in your browser, with DevTools → **Network** open.
2. Do anything that loads data (e.g. plan a trip), find a request to `…/metrobus-proxy/…`.
3. Copy the value of its **`Authorization`** header (the part after `Bearer `).

You'll pass this as the `METRO_JWT` environment variable below. It's long-lived but does
expire — if calls start returning `401`, grab a fresh one the same way.

## Add it to Claude

Replace `/ABSOLUTE/PATH/TO/metro-mcp` with where you cloned it, and `<TOKEN>` with your JWT.

### Claude Desktop

Edit `claude_desktop_config.json` (Settings → Developer → Edit Config):

```json
{
  "mcpServers": {
    "metro": {
      "command": "uv",
      "args": ["run", "--directory", "/ABSOLUTE/PATH/TO/metro-mcp", "python", "metro.py"],
      "env": { "METRO_JWT": "<TOKEN>" }
    }
  }
}
```

Restart Claude Desktop. The `metro` tools appear in the tools menu.

### Claude Code

```bash
claude mcp add metro --env METRO_JWT=<TOKEN> \
  -- uv run --directory /ABSOLUTE/PATH/TO/metro-mcp python metro.py
```

## Try it

Ask Claude: *"Find the stop id for Pettah, then plan a journey from there to Panadura tomorrow morning."*

## Notes

- `plan_journey` with an explicit `date` returns the full day's options; `now: true` returns
  only departures still upcoming from the current moment (empty late at night).
- Stop search is substring-based; a typed name must start matching a real stop name.
- This talks to Lanka Metro's own (unofficial) API. Use it responsibly.
