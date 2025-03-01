import os
import json
import httpx
import argparse
import uvicorn
from urllib.parse import urlparse
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://openrouter.ai/api/v2") # Changed to OpenRouter v2
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
DEFAULT_API_BASE = "https://openrouter.ai/"

# Command-line arguments
parser = argparse.ArgumentParser(description="OpenAI-compatible proxy server for OpenRouter")
parser.add_argument("--api-base", default=DEFAULT_API_BASE, help=f"API base URL (default: {DEFAULT_API_BASE})")
parser.add_argument("--host", default=DEFAULT_HOST, help=f"Host to bind to (default: {DEFAULT_HOST})")
parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port to bind to (default: {DEFAULT_PORT})")
def stream_response(response: httpx.Response):
    """Streams the response from OpenAI."""
    for chunk in response.iter_bytes():
        yield chunk

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def praoxy(path: str, request: Request):
    """Proxies requests to the OpenAI API."""
    url = f"{OPENAI_API_BASE}/{path}"
    headers = dict(request.headers)
    
    # Extract host from the target URL to set the Host header
    parsed_url = urlparse(OPENAI_API_BASE)
    headers["host"] = parsed_url.netloc
    print(headers)
    
    try:

        with httpx.Client() as client:
            response = client.request(
                method=request.method,
                url=url,
                headers=headers,
                params=request.query_params,
                content=request.body if request.method in ["POST", "PUT", "PATCH"] else None,
            )

        # Handle streaming responses
        if "text/event-stream" in response.headers.get("content-type", ""):
            return StreamingResponse(stream_response(response), media_type="text/event-stream")

        # Try parsing JSON, fallback to text
        try:
            return response.json()
        except json.JSONDecodeError:
            return response.text or {}

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        print(f"Proxy error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """Run the proxy server."""
    args = parser.parse_args()
    app.state.api_base = args.api_base
    
    print(f"Starting proxy server at http://{args.host}:{args.port}")
    print(f"Proxying requests to {args.api_base}")
    
    # Run the server
    uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
