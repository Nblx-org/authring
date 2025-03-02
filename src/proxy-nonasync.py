import os
import json
import httpx
import argparse
from flask import Flask, request, Response, stream_with_context
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Configuration with environment variable fallbacks
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
DEFAULT_API_BASE = "https://openrouter.ai/api/v1"

# Command-line arguments
parser = argparse.ArgumentParser(description="OpenAI-compatible proxy server for OpenRouter")
parser.add_argument("--api-base", default=DEFAULT_API_BASE, help=f"API base URL (default: {DEFAULT_API_BASE})")
parser.add_argument("--host", default=DEFAULT_HOST, help=f"Host to bind to (default: {DEFAULT_HOST})")
parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port to bind to (default: {DEFAULT_PORT})")
parser.add_argument("--verbose", action="store_true", help="Enable verbose logging of response content")

# Global variable to store API base URL
api_base = DEFAULT_API_BASE
verbose_logging = False

def stream_response(response):
    """Generator to stream and modify response data"""
    for chunk in response.iter_bytes():
        # For SSE (Server-Sent Events) responses from OpenAI-compatible APIs
        # Each chunk is typically a text line starting with "data: " followed by JSON
        try:
            # Decode the chunk to a string
            chunk_str = chunk.decode('utf-8')
            print(chunk_str)
            
            # Check if this is a data line in SSE format
            if chunk_str.startswith('data: '):
                # Extract the JSON part (after "data: ")
                json_str = chunk_str[6:]
                
                # Skip empty lines or "[DONE]" messages
                if json_str.strip() and json_str.strip() != '[DONE]':
                    # Parse the JSON
                    data = json.loads(json_str)
                    
                    # MODIFY THE RESPONSE HERE
                    # Example: Add a custom field to each chunk
                    if 'choices' in data and len(data['choices']) > 0:
                        # Access the content for different response formats
                        if 'delta' in data['choices'][0]:
                            # For streaming format
                            if 'content' in data['choices'][0]['delta']:
                                print(f"Streaming content: {data['choices'][0]['delta']['content']}")
                        elif 'message' in data['choices'][0]:
                            # For non-streaming format
                            if 'content' in data['choices'][0]['message']:
                                print(f"Message content: {data['choices'][0]['message']['content']}")
                    
                    # Convert back to JSON and format the SSE line
                    new_json_str = json.dumps(data)
                    chunk = f"data: {new_json_str}\n\n".encode('utf-8')
                    
                    print("Modified a chunk")
            
        except Exception as e:
            # If any error occurs during processing, log it but still pass through the original chunk
            print(f"Error processing chunk: {e}")
        
        # Yield the original or modified chunk
        yield chunk

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy(path):
    """Proxies requests to the OpenAI API."""
    global api_base
    url = f"{api_base}/{path}"
    
    # Copy headers from the request
    headers = dict(request.headers)
    
    # Extract host from the target URL to set the Host header
    parsed_url = urlparse(api_base)
    if 'Host' in headers:
        del(headers['Host'])

    headers["host"] = parsed_url.netloc
    
    print(f"Forwarding request to: {url}")
    
    try:
        # Get request body for methods that support it
        body = request.get_data() if request.method in ["POST", "PUT", "PATCH"] else None
        if body:
            print(f"Request body size: {len(body)} bytes")
            print(f"Request content type: {request.content_type}")
        
        # Use synchronous client with a reasonable timeout
        with httpx.Client(timeout=60.0) as client:
            print(json.dumps(json.loads(body), indent=4))
            response = client.request(
                method=request.method,
                url=url,
                headers=headers,
                params=request.args,
                content=body,
            )
            
        # For streaming responses
        if "text/event-stream" in response.headers.get("content-type", ""):
            print("Streaming response detected")
            return Response(
                stream_with_context(stream_response(response)),
                content_type="text/event-stream",
                headers={k: v for k, v in response.headers.items() if k.lower() not in ["transfer-encoding", "content-length"]}
            )
            
        # For regular responses
        print(f"Response status: {response.status_code}")
        print(f"Response content type: {response.headers.get('content-type')}")
        
        # Try returning as JSON if possible
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            return response.json(), response.status_code, {k: v for k, v in response.headers.items() 
                                                          if k.lower() not in ["transfer-encoding", "content-length"]}
        
        # Otherwise return as raw content
        return Response(
            response.content, 
            status=response.status_code,
            content_type=content_type,
            headers={k: v for k, v in response.headers.items() if k.lower() not in ["transfer-encoding", "content-length"]}
        )
            
    except httpx.HTTPStatusError as e:
        print(f"HTTP Status Error: {e}")
        return {"error": str(e), "detail": e.response.text}, e.response.status_code
    except Exception as e:
        print(f"Proxy error: {type(e).__name__}: {e}")
        return {"error": str(e)}, 500

def main():
    """Run the proxy server."""
    global api_base
    
    args = parser.parse_args()
    api_base = args.api_base
    
    print(f"Starting proxy server at http://{args.host}:{args.port}")
    print(f"Proxying requests to {api_base}")
    
    # Run the Flask server
    app.run(host=args.host, port=args.port, debug=True)

if __name__ == "__main__":
    main()
