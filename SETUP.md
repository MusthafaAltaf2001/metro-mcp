# Metro MCP — deploy on Vercel & share

Goal: a public HTTPS URL (`https://metro-app.musthafaaltaf.com/mcp`) that anyone
adds via Claude's **Add custom connector** button. No Anthropic approval needed.

## Files
- `metro.py`      — the server + tools (`plan_journey`, `search_stops`).
- `api/index.py`  — Vercel serverless entry: builds the ASGI app (stateless + json mode).
- `vercel.json`   — routes every request to that function.
- `requirements.txt` — the two deps Vercel installs (`mcp[cli]`, `httpx`).

> Vercel is serverless, not Docker — it runs `api/index.py` as a function, not a
> long-lived server. That's why there's no Dockerfile. The app is stateless so
> each request stands alone, which is exactly what serverless needs.

## Steps

1. **Push this folder to a GitHub repo.**

2. **Import it on Vercel:** vercel.com → **Add New → Project** → pick the repo →
   **Deploy**. Vercel detects `requirements.txt` + `api/` and builds the Python
   function. No build settings to change.

3. **Add your domain:** Project → **Settings → Domains** → add
   `metro-app.musthafaaltaf.com`. Vercel shows a DNS record to create.

4. **At your registrar** (musthafaaltaf.com), add the record Vercel gives you —
   usually:
       CNAME   metro-app   →   cname.vercel-dns.com
   Vercel auto-issues the TLS cert once DNS resolves (a few minutes).

5. **Done.** Your MCP URL is `https://metro-app.musthafaaltaf.com/mcp`.

## Verify (from your laptop)
    curl -s -X POST https://metro-app.musthafaaltaf.com/mcp \
      -H "Content-Type: application/json" \
      -H "Accept: application/json, text/event-stream" \
      -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"t","version":"1"}}}'
Expect a JSON result with `"serverInfo":{"name":"metro"...}`.

## How users install it (send them this)
1. claude.ai → **Settings → Connectors**
2. **Add custom connector**
3. Paste:  `https://metro-app.musthafaaltaf.com/mcp`
4. Save. The `plan_journey` and `search_stops` tools appear.

Requires a paid Claude plan (Pro/Max/Team/Enterprise); Free tier has no
custom-connector button.

## Notes
- The metro JWT in `metro.py` expires **2027-03-27** — every user breaks at once
  when it lapses. Re-grab it from the site and redeploy (or set `METRO_JWT` as a
  Vercel env var instead of hardcoding).
- Free Vercel functions have a short execution limit; these calls return in ~1s,
  well under it.
