# Authring

[![PyPI version](https://img.shields.io/pypi/v/authring.svg)](https://pypi.org/project/authring/)

Authring is an MCP-driven guardrails system that evaluates code modification proposals based on historical impact, contributor expertise, and production risk assessment. The system utilizes:

- **Astra DB** for historical data storage
- **Unstructured.io** for document parsing
- **Langflow** for AI-driven decision-making
- **Twilio** for real-time human validation
- **GitHub CLI (gh)** for managing patch review links

## Workflow
1. **MCP Server** receives a proposed patch in the format:
   ```json
   {
       "repo": "flight-control",
       "purpose": "Fix typo in logging message",
       "patch": "diff --git a/utils/logger.py b/utils/logger.py\n- log.info('Engne diagnostics running')\n+ log.info('Engine diagnostics running')"
   }
   ```
2. **Contextualization**: The system extracts metadata from `mock/code/` to determine the impact, authorship, and production status of the affected code.
3. **Risk Assessment**:
   - If **Safe**, the patch is accepted.
   - If **Unsafe**, the patch is rejected.
   - If **Maybe**, a **Twilio notification** is sent to the responsible contributor.
4. **Twilio Review (Maybe Cases)**:
   - The contributor receives a text:
     ```
     Authring wants to 'Improve flight path prediction' by changing 'navigation.py'.
     Review it here: <GitHub Gist Link> and respond with your recommendation.
     ```
   - The system waits for a response (15s timeout) before making a final decision.

## Demo Scenarios
- ✅ **Valid Purpose, Valid Patch**: Fix typo in `logger.py`.
- ❌ **Invalid Purpose**: Replace autopilot with `YOLO()` function.
- ⚠️ **Valid Purpose, Invalid Patch**: Change flight path prediction logic (triggers Twilio).

## Setup
```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python mcp_server.py
```

## Running the Demo
```sh
python train.py  # Populate mock Astra DB with training data
python mcp_server.py  # Start the evaluation pipeline
```

