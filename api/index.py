import os
import sys

# ponytail: put repo root on the path so `metro` imports on Vercel's serverless runtime.
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from metro import mcp  # noqa: E402

# Serverless-safe: stateless (no cross-request session) + json_response (no SSE stream to time out).
_mcp_app = mcp.streamable_http_app(
    stateless_http=True, json_response=True, streamable_http_path="/mcp"
)


# Vercel's rewrite forwards every request to this function as path "/api/index",
# not the original "/mcp" (confirmed in deploy logs). Normalize the path so it
# always hits the MCP route, whatever Vercel forwards.
# ponytail: 4-line ASGI shim beats guessing Vercel's rewrite path behavior.
async def app(scope, receive, send):
    if scope["type"] == "http":
        scope = dict(scope)
        scope["path"] = "/mcp"
        scope["raw_path"] = b"/mcp"
    await _mcp_app(scope, receive, send)
