import os
import sys

# ponytail: put repo root on the path so `metro` imports on Vercel's serverless runtime.
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from metro import mcp  # noqa: E402

# Serverless-safe: stateless (no cross-request session) + json_response (no SSE stream to time out).
app = mcp.streamable_http_app(
    stateless_http=True, json_response=True, streamable_http_path="/mcp"
)
