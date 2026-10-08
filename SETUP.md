# Metro MCP — deploy on Vercel & share

Goal: a public HTTPS URL (`https://lmt-mcp.musthafaaltaf.com/mcp`) that anyone
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
   `lmt-mcp.musthafaaltaf.com`. Vercel shows a DNS record to create.

4. **In your DNS provider** — for musthafaaltaf.com that's **Cloudflare** (the domain
   is registered at GoDaddy but DNS is managed by Cloudflare). Add the record Vercel
   gives you, usually:
       CNAME   lmt-mcp   →   cname.vercel-dns.com
   Set the Cloudflare proxy to **DNS only (grey cloud)**, not Proxied, or Vercel can't
   issue the cert. Vercel auto-issues TLS once DNS resolves (a few minutes).

5. **Done.** Your MCP URL is `https://lmt-mcp.musthafaaltaf.com/mcp`.

## Verify (from your laptop)
    curl -s -X POST https://lmt-mcp.musthafaaltaf.com/mcp \
      -H "Content-Type: application/json" \
      -H "Accept: application/json, text/event-stream" \
      -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"t","version":"1"}}}'
Expect a JSON result with `"serverInfo":{"name":"metro"...}`.

## How users install it (send them this)
1. claude.ai → **Settings → Connectors**
2. **Add custom connector**
3. Paste:  `https://lmt-mcp.musthafaaltaf.com/mcp`
4. Save. The `plan_journey` and `search_stops` tools appear.

Requires a paid Claude plan (Pro/Max/Team/Enterprise); Free tier has no
custom-connector button.

## Notes
- The metro JWT is read from the `METRO_JWT` env var (set in Vercel → Settings →
  Environment Variables; not in the code). It expires **2027-03-27** — every user
  breaks at once when it lapses. Re-grab it from the site, update the env var, redeploy.
- Free Vercel functions have a short execution limit; these calls return in ~1s,
  well under it.
