import os
from typing import List
from twilio.rest import Client
import mcp.types as types
import click
from mcp.server.lowlevel import Server
import anyio
from pydantic import FileUrl

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_API_KEY = os.getenv("TWILIO_API_KEY")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

if not TWILIO_API_KEY or not TWILIO_ACCOUNT_SID or not TWILIO_PHONE_NUMBER:
    raise ValueError("Twilio environment variables not set (TWILIO_API_KEY, TWILIO_ACCOUNT_SID, TWILIO_PHONE_NUMBER)")

twilio_client = Client(TWILIO_API_KEY, "", account_sid=TWILIO_ACCOUNT_SID)

app = Server("patch-validator")
sent_messages = []  # Store (to_number, message_sid) tuples


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="validate_patch",
            description="Validate the purpose, patch, and base code folder.",
            inputSchema={
                "type": "object",
                "properties": {
                    "base_code_folder": {
                        "type": "string",
                        "description": "The folder of the code being patched",
                    },
                    "purpose": {
                        "type": "string",
                        "description": "Brief description of what the patch does",
                    },
                    "patch": {
                        "type": "string",
                        "description": "The actual patch content",
                    },
                },
                "required": ["base_code_folder", "purpose", "patch"],
            },
        )
    ]


@app.call_tool()
async def call_tool(tool_name: str, arguments: dict) -> str | dict | list:
    if tool_name == "validate_patch":
        return "This change is forbidden by policy"  # Still returning the stubbed response
    elif tool_name == "send_sms":
        return await send_sms(arguments)
    elif tool_name == "check_sms_replies":
        return await check_sms_replies(arguments)
    else:
        raise ValueError(f"Unknown tool: {tool_name}")


async def send_sms(to_number: str, message_body: str) -> str:
    """Sends an SMS message using Twilio."""
    try:
        message = twilio_client.messages.create(
            to=to_number,
            from_=TWILIO_PHONE_NUMBER,
            body=message_body
        )
        sent_messages.append((to_number, message.sid, message.date_created))
        return f"Message sent to {to_number}. SID: {message.sid}"
    except Exception as e:
        return f"Error sending SMS: {str(e)}"

async def check_sms_replies(to_number: str) -> List[str]:
    """Checks for replies to SMS messages sent to a specific number."""
    replies = []
    for sent_to, sent_sid, sent_time in sent_messages:
        if sent_to != to_number:
            continue

        messages = twilio_client.messages.list(
            to=TWILIO_PHONE_NUMBER,
            from_=to_number  # Check for messages from the user to our Twilio number
        )
        for message in messages:
            if message.date_created > sent_time:
                replies.append(f"Reply from {message.from_}: {message.body}")
    return replies

@mcp.tool()
async def validate_patch(patch_info: dict) -> str:
    """
    Validate the purpose, patch, and base code folder using Langflow.
    
    Expected input format:
    {
        "base_code_folder": "The folder of the code being patched",
        "purpose": "Brief description of what the patch does",
        "patch": "The actual patch content"
    }
    """
    base_code_folder = patch_info.get("base_code_folder", "")
    purpose = patch_info.get("purpose", "")
    patch = patch_info.get("patch", "")

    #result = await langflow.validate_proposal(purpose, patch, base_code_folder)

    if IS_DEMO and result["status"] == "warning":
        async with httpx.AsyncClient() as client:
            await client.post(TWILIO_WEBHOOK_URL, json={"message": "Reviewer approval required for patch"})
        return "Demo mode: Triggered Twilio notification."

    return "This change is forbidden by policy"
    #return result["message"]

SAMPLE_RESOURCES = {
    "greeting": "Hello! This is a sample text resource.",
    "help": "This server provides a few sample text resources for testing.",
    "about": "This is the simple-resource MCP server implementation.",
}
@click.command()
@click.option("--port", default=8000, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)
def main(port: int, transport: str) -> int:
    app = Server("mcp-simple-resource")

    @app.list_resources()
    async def list_resources() -> list[types.Resource]:
        return [
            types.Resource(
                uri=FileUrl(f"file:///{name}.txt"),
                name=name,
                description=f"A sample text resource named {name}",
                mimeType="text/plain",
            )
            for name in SAMPLE_RESOURCES.keys()
        ]

    @app.read_resource()
    async def read_resource(uri: FileUrl) -> str | bytes:
        name = uri.path.replace(".txt", "").lstrip("/")

        if name not in SAMPLE_RESOURCES:
            raise ValueError(f"Unknown resource: {uri}")

        return SAMPLE_RESOURCES[name]

    if transport == "sse":
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        srom starlette.routing import Mount, Route

        sse = SseServerTransport("/messages/")

        async def handle_sse(request):
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )

        starlette_app = Starlette(
            debug=True,
            routes=[
                Route("/sse", endpoint=handle_sse),
                Mount("/messages/", app=sse.handle_post_message),
            ],
        )

        import uvicorn

        uvicorn.run(starlette_app, host="0.0.0.0", port=port)
    else:
        from mcp.server.stdio import stdio_server

        async def arun():
            async with stdio_server() as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )

        anyio.run(arun)

    return 0

