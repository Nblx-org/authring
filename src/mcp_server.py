from fastmcp import FastMCP
import httpx
import os
from typing import Dict, Optional, List
from twilio.rest import Client



import dotenv

dotenv.load_dotenv()
mcp = FastMCP("Patch Validator 🔍")

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_API_KEY = os.getenv("TWILIO_API_KEY")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

if not TWILIO_API_KEY or not TWILIO_ACCOUNT_SID or not TWILIO_PHONE_NUMBER:
    raise ValueError("Twilio environment variables not set (TWILIO_API_KEY, TWILIO_ACCOUNT_SID, TWILIO_PHONE_NUMBER)")

twilio_client = Client(TWILIO_API_KEY, "", account_sid=TWILIO_ACCOUNT_SID)


# Configuration
LANGFLOW_URL = "http://localhost:7860"  # Default Langflow port
LANGFLOW_API_KEY = None  # If authentication is required
IS_DEMO = True  # Toggle demo mode

class LangflowClient:
    """Client for interacting with Langflow API"""
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    async def validate_proposal(self, purpose: str, patch: str, base_code_folder: str) -> Dict:
        """
        TODO: Implement real Langflow communication
        This would send the purpose, patch and base_code_folder to a Langflow flow designed to validate them

        The Langflow flow should:
        1. Analyze the base_code_folder, purpose for clarity and validity
        2. Check if the patch aligns with the stated purpose
        3. Validate the patch syntax and potential impact
        4. Return a structured response with validation results
        """
        """Sends validation request to Langflow or returns a stubbed response in demo mode."""
        if IS_DEMO:
            return {"status": "warning", "message": "valid purpose, uncertain patch - contacting reviewer"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/process",  # Actual Langflow endpoint
                    headers=self.headers,
                    json={
                        "base_code_folder": base_code_folder,
                        "purpose": purpose,
                        "patch": patch,
                    }
                )
                return response.json()

            # For now, return a mock response
            if not base_code_folder or not purpose:
                return {"status": "error", "message": "invalid base_code_folder or purpose"}

            if "bug fix" in purpose.lower():
                if "fix" in patch.lower():
                    return {"status": "success", "message": "Valid purpose, valid patch"}
                return {"status": "warning", "message": "valid purpose, invalid patch (make a new proposal)"}

            return {"status": "error", "message": "invalid purpose"}

        except Exception as e:
            return {"status": "error", "message": f"Langflow validation failed: {str(e)}"}


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




    #    return "Demo mode: Triggered Twilio notification."

    #return result["message"]

sent_messages = []  # Store (to_number, message_sid) tuples

@mcp.tool()
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

@mcp.tool()
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

if __name__ == "__main__":
    mcp.run()
