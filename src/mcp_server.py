from fastmcp import FastMCP
import httpx
import os
from typing import Dict, Optional

# Configuration
LANGFLOW_URL = "http://localhost:7860"  # Default Langflow port
LANGFLOW_API_KEY = None  # If authentication is required
TWILIO_WEBHOOK_URL = os.getenv("TWILIO_WEBHOOK_URL", "http://localhost:5000/twilio_mock")  # Mock webhook for Twilio
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

# Initialize Langflow client
langflow = LangflowClient(LANGFLOW_URL, LANGFLOW_API_KEY)

mcp = FastMCP("Patch Validator 🔍")

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

    result = await langflow.validate_proposal(purpose, patch, base_code_folder)

    if IS_DEMO and result["status"] == "warning":
        async with httpx.AsyncClient() as client:
            await client.post(TWILIO_WEBHOOK_URL, json={"message": "Reviewer approval required for patch"})
        return "Demo mode: Triggered Twilio notification."

    return result["message"]

