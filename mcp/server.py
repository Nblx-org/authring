#!/usr/bin/env python3

from fastmcp import FastMCP
mcp = FastMCP("Demo 🚀")


@mcp.tool()
def validate_patch(patch_info: dict) -> str:
    """Validate the purpose and patch"""
    purpose = patch_info.get("purpose")
    patch = patch_info.get("patch")

    if not purpose:
        return "invalid purpose"

    if not patch:
        return "valid purpose, invalid patch (make a new proposal)"

    return "Valid purpose, valid patch"
