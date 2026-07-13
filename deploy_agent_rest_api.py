#!/usr/bin/env python3
"""
Deploy invoice agent to Azure AI Foundry using REST API.
Comprehensive production-ready deployment script.
"""

import os
import json
import sys
import time
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# Configuration
WORKSPACE_DIR = Path(__file__).parent
FOUNDRY_ENDPOINT = "https://tagoreautomation-2862-resource.services.ai.azure.com"
PROJECT_ID = "tagoreautomation-2862"
AGENT_NAME = "invoice-agent"
FUNCTION_ENDPOINT = "https://invoice-agent-docintelligence2.azurewebsites.net"
FUNCTION_KEY = "<AZURE_FUNCTION_KEY>"

# Deployment logs
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = WORKSPACE_DIR / f"agent_deployment_{TIMESTAMP}.log"
RESULT_FILE = WORKSPACE_DIR / "DEPLOYMENT_SUCCESS.md"

def log(msg, level="INFO"):
    """Log message to console and file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {level}: {msg}"
    print(log_msg)
    with open(LOG_FILE, "a") as f:
        f.write(log_msg + "\n")

def section(title):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")

def step(num, total, msg):
    """Print step"""
    print(f"\n[Step {num}/{total}] {msg}")


def resolve_az_cli():
    """Resolve Azure CLI executable path reliably on Windows and non-Windows."""
    # First try the current process PATH.
    for candidate in ("az", "az.cmd", "az.exe"):
        found = shutil.which(candidate)
        if found:
            return found

    # On Windows, VS Code/Python processes can have stale PATH. Refresh from env vars.
    if os.name == "nt":
        machine_path = os.environ.get("PATH", "")
        try:
            import winreg  # pylint: disable=import-error

            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment") as key:
                sys_path, _ = winreg.QueryValueEx(key, "Path")
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as key:
                user_path, _ = winreg.QueryValueEx(key, "Path")
            merged_path = f"{sys_path};{user_path};{machine_path}"
            os.environ["PATH"] = merged_path
        except Exception:
            # Registry lookup can fail in restricted contexts; continue with fallbacks.
            pass

        for candidate in ("az", "az.cmd", "az.exe"):
            found = shutil.which(candidate)
            if found:
                return found

        # Common default install locations.
        known_locations = [
            r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",
            r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",
            r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.exe",
        ]
        for location in known_locations:
            if Path(location).exists():
                return location

    return None

def get_access_token():
    """Get Azure access token using Azure CLI"""
    step(1, 6, "Obtaining Azure Access Token")
    
    try:
        # Try to get token with Foundry resource audience
        az_cli = resolve_az_cli()
        if not az_cli:
            raise FileNotFoundError("Azure CLI executable not found")

        print(f"âœ“ Using Azure CLI: {az_cli}")

        cmd = [
            az_cli, "account", "get-access-token",
            "--resource", "https://ai.azure.com",
            "--query", "accessToken",
            "-o", "tsv"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.strip()
            print(f"âŒ Failed to get token: {error_msg}")
            print("\nðŸ’¡ To get token manually, run:")
            print("   az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv")
            sys.exit(1)
        
        token = result.stdout.strip()
        if not token:
            raise ValueError("No token returned")
        
        # Verify token format (JWT)
        if token.count('.') != 2:
            raise ValueError("Invalid token format (not JWT)")
        
        print(f"âœ“ Token obtained successfully")
        print(f"  Token: {token[:20]}...{token[-20:]}")
        log(f"Access token obtained")
        
        return token
        
    except FileNotFoundError:
        print("âŒ Azure CLI not found")
        print("   Please install: https://learn.microsoft.com/cli/azure/install-azure-cli")
        sys.exit(1)
    except Exception as e:
        print(f"âŒ Error: {e}")
        sys.exit(1)

def prepare_agent_payload():
    """Prepare agent deployment payload"""
    step(2, 6, "Preparing Agent Configuration")
    
    # Load manifest if exists
    manifest_file = WORKSPACE_DIR / "agent_manifest.yaml"
    instructions = """You are an AI data extraction and classification agent specializing in real estate property management invoices.

Your task is to analyze the text or layout data of the vendor invoice provided and extract key accounting details.

Output your response strictly in the following JSON format:
{
    \"property_name\": \"Name of the managed apartment complex, building, or address\",
    \"vendor_name\": \"The service provider or vendor company name\",
    \"invoice_category\": \"Select ONE: [Utilities, Landscaping/Grounds, Plumbing, HVAC, Electrical, General Maintenance, Cleaning/Janitorial, Legal/Professional, Office Supplies, Other]\",
    \"invoice_number\": \"Invoice reference number or string\",
    \"invoice_date\": \"YYYY-MM-DD\",
    \"total_amount\": 0.00,
    \"currency\": \"USD\"
}

If a field cannot be found, set its value to null. Do not include any markdown formatting wrappers or extra conversational text outside of the JSON block."""
    
    if manifest_file.exists():
        try:
            import yaml

            with open(manifest_file) as f:
                manifest = yaml.safe_load(f)
            instructions = manifest.get("instructions", instructions)
            print(f"âœ“ Loaded manifest: {manifest.get('name')}")
        except ModuleNotFoundError:
            print("âš  pyyaml not installed, using default instructions")
            log("pyyaml missing; proceeding with default instructions", "WARNING")
    
    # Create agent payload
    payload = {
        "name": AGENT_NAME,
        "description": "Invoice extraction and analysis using Azure Document Intelligence and OpenAPI integration",
        # v1/vNext agents API expects a nested definition object.
        "definition": {
            "kind": "prompt",
            "model": "gpt-5-mini",
            "instructions": instructions,
        },
        # Keep legacy flat fields for older API compatibility.
        "model": "gpt-5-mini",
        "instructions": instructions,
        "backend": {
            "type": "http",
            "url": f"{FUNCTION_ENDPOINT}/api/invoice",
            "auth": {
                "type": "header",
                "headerName": "x-functions-key",
                "headerValue": FUNCTION_KEY
            }
        },
        "tools": [
            {
                "type": "openapi",
                "name": "invoice_processor",
                "description": "Extracts invoice data using Azure Document Intelligence",
                "spec": {
                    "openapi": "3.0.0",
                    "info": {
                        "title": "Invoice Processor",
                        "version": "1.0.0"
                    },
                    "servers": [
                        {"url": FUNCTION_ENDPOINT}
                    ],
                    "paths": {
                        "/api/invoice": {
                            "post": {
                                "operationId": "processInvoice",
                                "description": "Process invoice and extract structured data",
                                "requestBody": {
                                    "required": True,
                                    "content": {
                                        "application/json": {
                                            "schema": {
                                                "type": "object",
                                                "properties": {
                                                    "text": {"type": "string", "description": "Invoice text"}
                                                },
                                                "required": ["text"]
                                            }
                                        }
                                    }
                                },
                                "responses": {
                                    "200": {
                                        "description": "Extracted invoice data",
                                        "content": {
                                            "application/json": {
                                                "schema": {
                                                    "type": "object",
                                                    "properties": {
                                                        "extracted_fields": {"type": "object"},
                                                        "analysis": {"type": "object"}
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        ]
    }
    
    print(f"âœ“ Agent name: {payload['name']}")
    print(f"âœ“ Model: {payload['model']}")
    print(f"âœ“ Tools: {len(payload.get('tools', []))} configured")
    print(f"âœ“ Backend: {payload['backend']['url']}")
    log(f"Agent configuration prepared")
    
    return payload

def deploy_agent(token, payload):
    """Deploy agent via REST API"""
    step(3, 6, "Deploying Agent to Azure AI Foundry")
    
    # Build API endpoint candidates (Foundry APIs vary by route/version).
    endpoint_candidates = [
        f"{FOUNDRY_ENDPOINT}/api/projects/{PROJECT_ID}/agents?api-version=2025-05-01",
        f"{FOUNDRY_ENDPOINT}/api/projects/{PROJECT_ID}/agents?api-version=2025-05-15-preview",
        f"{FOUNDRY_ENDPOINT}/api/projects/{PROJECT_ID}/agents?api-version=v1",
        f"{FOUNDRY_ENDPOINT}/api/projects/{PROJECT_ID}/agents?api-version=2024-10-01-preview",
        f"{FOUNDRY_ENDPOINT}/api/projects/{PROJECT_ID}/agents?api-version=2024-05-01-preview",
        f"{FOUNDRY_ENDPOINT}/projects/{PROJECT_ID}/agents?api-version=2024-12-01-preview",
    ]
    
    print("Method: POST")
    
    # Prepare headers
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Prepare request
    for url in endpoint_candidates:
        print(f"Endpoint: {url}")
        request = Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method="POST"
        )

        try:
            print("Sending deployment request...")

            with urlopen(request) as response:
                status = response.status
                body = response.read().decode('utf-8')
                result = json.loads(body)

                print(f"âœ“ Status: {status} OK")
                print(f"âœ“ Agent created successfully!")

                agent_id = result.get("id") or result.get("name", AGENT_NAME)
                print(f"âœ“ Agent ID: {agent_id}")

                log(f"Agent deployed successfully (ID: {agent_id})")

                return {
                    "success": True,
                    "id": agent_id,
                    "name": result.get("name"),
                    "status": result.get("status", "created"),
                    "url": f"https://ai.azure.com/projects/{PROJECT_ID}/agents/{agent_id}"
                }

        except HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f"âŒ HTTP {e.code}: {e.reason}")
            print(f"   Response: {error_body[:200]}")
            log(f"Deployment attempt failed for {url} (HTTP {e.code}): {error_body}", "ERROR")

            if e.code == 409 and "already exists" in error_body.lower():
                print("âœ“ Agent already exists; treating as successful deployment")
                log("Agent already exists; returning existing resource", "INFO")
                return {
                    "success": True,
                    "id": AGENT_NAME,
                    "name": AGENT_NAME,
                    "status": "existing",
                    "url": f"https://ai.azure.com/projects/{PROJECT_ID}/agents/{AGENT_NAME}"
                }

            # Continue trying endpoint fallbacks on common route/version failures.
            if e.code in (400, 404):
                print("   Trying next endpoint/version fallback...")
                continue

            try:
                error_json = json.loads(error_body)
                error_msg = error_json.get("error", {}).get("message", error_body)
                print(f"   Error: {error_msg}")
            except Exception:
                pass

            return {"success": False, "error": f"HTTP {e.code}"}

        except URLError as e:
            print(f"âŒ Connection error: {e.reason}")
            log(f"Connection error for {url}: {e}", "ERROR")
            continue

    return {"success": False, "error": "No valid Foundry endpoint/api-version combination succeeded"}

def verify_deployment(token, agent_id):
    """Verify agent was deployed"""
    step(4, 6, "Verifying Deployment")
    
    headers = {"Authorization": f"Bearer {token}"}

    endpoint_candidates = [
        f"{FOUNDRY_ENDPOINT}/api/projects/{PROJECT_ID}/agents/{agent_id}?api-version=2025-05-01",
        f"{FOUNDRY_ENDPOINT}/api/projects/{PROJECT_ID}/agents/{agent_id}?api-version=2025-05-15-preview",
        f"{FOUNDRY_ENDPOINT}/api/projects/{PROJECT_ID}/agents/{agent_id}?api-version=v1",
        f"{FOUNDRY_ENDPOINT}/api/projects/{PROJECT_ID}/agents/{agent_id}?api-version=2024-10-01-preview",
        f"{FOUNDRY_ENDPOINT}/api/projects/{PROJECT_ID}/agents/{agent_id}?api-version=2024-05-01-preview",
        f"{FOUNDRY_ENDPOINT}/projects/{PROJECT_ID}/agents/{agent_id}?api-version=2024-12-01-preview",
    ]

    for url in endpoint_candidates:
        try:
            request = Request(url, headers=headers, method="GET")
            with urlopen(request) as response:
                result = json.loads(response.read().decode('utf-8'))
                latest = result.get("versions", {}).get("latest", {})
                model_name = latest.get("definition", {}).get("model") or result.get("model", "unknown")

                print(f"âœ“ Agent found: {result.get('name')}")
                print(f"âœ“ Status: {result.get('status', 'active')}")
                print(f"âœ“ Model: {model_name}")

                return True
        except Exception:
            continue

    print("âš  Could not verify via API (agent may still be visible in Foundry UI)")
    log("Verification note: all verify endpoint fallbacks failed")
    return None

def create_summary(deployment_result):
    """Create deployment summary document"""
    step(5, 6, "Generating Summary")
    
    summary = f"""# Agent Deployment Successful

**Deployment Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Agent Details

| Field | Value |
|-------|-------|
| **Name** | {deployment_result.get('name', AGENT_NAME)} |
| **ID** | {deployment_result.get('id')} |
| **Status** | {deployment_result.get('status', 'Created')} |
| **Project** | {PROJECT_ID} |
| **Endpoint** | {FOUNDRY_ENDPOINT} |

---

## Access Your Agent

ðŸ”— **Foundry UI:** [{deployment_result.get('url')}]({deployment_result.get('url')})

---

## Integrated Tools

### Invoice Processor (OpenAPI)
- **Endpoint:** {FUNCTION_ENDPOINT}/api/invoice
- **Method:** POST
- **Authentication:** x-functions-key header
- **Description:** Extracts structured invoice data using Azure Document Intelligence

#### Request Example
```json
{{
  "text": "Invoice #INV-2024-001\\nVendor: Acme Corp\\nDate: 2024-07-10\\nTotal: $1,500.00"
}}
```

#### Response Example
```json
{{
  "extracted_fields": {{
    "vendor_name": "Acme Corp",
    "invoice_number": "INV-2024-001",
    "total_amount": 1500.00,
    "invoice_date": "2024-07-10"
  }},
  "analysis": {{
    "confidence_score": 0.95,
    "document_type": "invoice"
  }}
}}
```

---

## Next Steps

1. **Test in Playground**
   - Go to agent URL above
   - Click "Playground" or "Test" tab
   - Send sample invoice text
   - Verify extraction works correctly

2. **Monitor Execution**
   - Check agent logs and traces
   - Monitor token usage
   - Track confidence scores

3. **Iterate & Improve**
   - Refine agent instructions if needed
   - Update tool configurations
   - Add more tools if required

4. **Production Ready**
   - Once verified, publish for end users
   - Set up monitoring and alerts
   - Document API contracts

---

## Troubleshooting

### Agent Not Visible in UI
- Wait 30 seconds for propagation
- Refresh Foundry page
- Check project settings

### Tool Not Responding
- Verify Function endpoint: {FUNCTION_ENDPOINT}/api/invoice
- Test function directly with curl or Python
- Check function key and authentication

### Token Errors
- Token may have expired
- Regenerate: `az account get-access-token --resource https://ai.azure.com`
- Ensure correct subscription set

---

## Configuration Files

All deployment files preserved for reference:

| File | Purpose |
|------|---------|
| `agent_manifest.yaml` | Agent definition |
| `openapi_schema.json` | Tool OpenAPI spec |
| `agent_deployment_config.json` | Complete config |
| `SDK_DEPLOYMENT_GUIDE.md` | Detailed guide |
| `AGENT_BUILD_PLAN.md` | Phase plan |

---

## Logs

Deployment log: `{LOG_FILE}`

---

**Status:** âœ… Deployed Successfully  
**Created:** {datetime.now().isoformat()}  
"""
    
    # Save summary
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        f.write(summary)
    
    print(f"âœ“ Summary saved: {RESULT_FILE}")
    print(summary)
    
    log("Deployment complete")
    
    return summary

def main():
    """Main deployment orchestration"""
    section("INVOICE AGENT DEPLOYMENT TO AZURE AI FOUNDRY")
    
    print(f"Start: {datetime.now()}")
    print(f"Project: {PROJECT_ID}")
    print(f"Agent: {AGENT_NAME}")
    print(f"Log: {LOG_FILE}\n")
    
    try:
        # Get token
        token = get_access_token()
        
        # Prepare configuration
        payload = prepare_agent_payload()
        
        # Deploy
        deployment_result = deploy_agent(token, payload)
        
        if not deployment_result.get("success"):
            print(f"\nâŒ Deployment failed: {deployment_result.get('error')}")
            print(f"\nðŸ’¡ Troubleshooting tips:")
            print(f"  â€¢ Verify token is valid")
            print(f"  â€¢ Check Foundry endpoint: {FOUNDRY_ENDPOINT}")
            print(f"  â€¢ Verify project ID: {PROJECT_ID}")
            print(f"  â€¢ Try different API version")
            return 1
        
        # Verify
        verify_deployment(token, deployment_result.get("id"))
        
        # Summary
        create_summary(deployment_result)
        
        step(6, 6, "Deployment Complete")
        print(f"\nâœ… Agent successfully deployed!")
        print(f"\nURL: {deployment_result.get('url')}")
        print(f"ID: {deployment_result.get('id')}")
        
        print("\nEnd: " + datetime.now().isoformat())
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nâš  Deployment cancelled by user")
        return 1
    except Exception as e:
        print(f"\nâŒ Unexpected error: {e}")
        log(f"Unexpected error: {e}", "ERROR")
        return 1


if __name__ == "__main__":
    sys.exit(main())

