from fastmcp import FastMCP
import httpx
from typing import Dict, Optional

# TODO: Configure these in environment variables or config file
LANGFLOW_URL = "http://localhost:7860"  # Default Langflow port
LANGFLOW_API_KEY = None  # If authentication is required

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
        try:
            # Stubbed response - in reality, this would make an async HTTP request to Langflow
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

    # Get validation result from Langflow
    result = await langflow.validate_proposal(purpose, patch, base_code_folder)

    return result["message"]
