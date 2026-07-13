#!/usr/bin/env python3
"""
Azure AI Foundry Agent Deployment Script
Deploys the invoice-agent to Azure AI Foundry with HTTP backend
"""

import json
import os
import subprocess
import sys
from datetime import datetime

# Configuration
AGENT_NAME = "invoice-agent"
AGENT_DESCRIPTION = "Invoice extraction and analysis using Document Intelligence"
FUNCTION_ENDPOINT = "https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice"
FUNCTION_KEY = None  # Will be set from parameter
FOUNDRY_PROJECT_URL = None  # Will be set from parameter
RESOURCE_GROUP = "rmtag-openai-agents-rg"
SUBSCRIPTION = "d65af6df-c048-43eb-8cfd-ea54c482e516"

# Input/Output Schemas
INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "text": {
            "type": "string",
            "description": "Invoice text to analyze"
        },
        "file_path": {
            "type": "string",
            "description": "Path to invoice file (optional)"
        }
    }
}

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "extracted_fields": {
            "type": "object",
            "properties": {
                "vendor_name": {"type": "string"},
                "invoice_number": {"type": "string"},
                "total_amount": {"type": "number"},
                "invoice_date": {"type": "string"}
            }
        },
        "analysis": {
            "type": "object",
            "properties": {
                "document_type": {"type": "string"},
                "confidence": {"type": "number"},
                "vendor_name": {"type": "string"},
                "invoice_number": {"type": "string"},
                "total_amount": {"type": "number"},
                "invoice_date": {"type": "string"},
                "issues": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }
    }
}

def log(message, level="INFO"):
    """Print formatted log message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def run_command(cmd, description=""):
    """Run a shell command and return output"""
    if description:
        log(description)
    try:
        # On Windows, try to find az.cmd in Program Files
        if sys.platform == "win32" and cmd[0] == "az":
            import shutil
            az_path = shutil.which("az.cmd") or shutil.which("az") or "C:\\Program Files\\Azure CLI\\bin\\az.cmd"
            cmd[0] = az_path
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, shell=sys.platform == "win32")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        log(f"Command failed: {e.stderr}", "ERROR")
        raise

def get_access_token(resource="https://ai.azure.com"):
    """Get Azure access token"""
    log("Getting Azure access token...")
    cmd = [
        "az", "account", "get-access-token",
        "--resource", resource,
        "--query", "accessToken",
        "-o", "tsv"
    ]
    token = run_command(cmd)
    if not token:
        raise Exception("Failed to get access token. Ensure you're logged in with 'az login'")
    log(f"✓ Token obtained (length: {len(token)} chars)")
    return token

def create_agent_via_api(token, foundry_url, function_key):
    """Create agent in Azure AI Foundry via REST API"""
    log("Creating agent in Azure AI Foundry...", "STEP")
    
    # Prepare agent payload
    agent_payload = {
        "name": AGENT_NAME,
        "description": AGENT_DESCRIPTION,
        "kind": "Agent",
        "spec": {
            "kind": "default",
            "endpoints": [
                {
                    "kind": "endpoint",
                    "type": "http",
                    "url": FUNCTION_ENDPOINT,
                    "auth": {
                        "type": "header",
                        "key": "x-functions-key",
                        "value": function_key
                    }
                }
            ],
            "inputSchema": INPUT_SCHEMA,
            "outputSchema": OUTPUT_SCHEMA
        }
    }
    
    # Clean up Foundry URL (remove /api/projects if present)
    base_url = foundry_url.replace("/api/projects/", "/").rsplit("/", 1)[0]
    project_id = foundry_url.split("/")[-1] if "/" in foundry_url else ""
    
    # Try different API endpoints
    endpoints = [
        f"{base_url}/agents",
        f"{foundry_url}/agents",
        f"{base_url}/api/agents",
    ]
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    import requests
    
    for endpoint in endpoints:
        try:
            log(f"Trying endpoint: {endpoint}")
            resp = requests.post(endpoint, json=agent_payload, headers=headers, timeout=30)
            
            if resp.status_code in [200, 201, 202]:
                log(f"✓ Agent created successfully! Status: {resp.status_code}", "SUCCESS")
                result = resp.json()
                return result
            elif resp.status_code == 409:
                log(f"Agent already exists (409). Updating instead...", "WARNING")
                # Try to update
                agent_id = AGENT_NAME.lower().replace(" ", "-")
                update_endpoint = f"{endpoint}/{agent_id}"
                resp = requests.patch(update_endpoint, json=agent_payload, headers=headers, timeout=30)
                if resp.status_code in [200, 201]:
                    log(f"✓ Agent updated successfully!", "SUCCESS")
                    return resp.json()
            else:
                log(f"Endpoint {endpoint} failed with {resp.status_code}: {resp.text[:200]}", "WARNING")
                continue
                
        except Exception as e:
            log(f"Error with endpoint {endpoint}: {str(e)}", "WARNING")
            continue
    
    raise Exception(f"Failed to create agent. Tried endpoints: {endpoints}")

def verify_agent_deployment(token, foundry_url, agent_name):
    """Verify the agent was created"""
    log("Verifying agent deployment...", "STEP")
    
    import requests
    
    base_url = foundry_url.replace("/api/projects/", "/").rsplit("/", 1)[0]
    endpoint = f"{base_url}/agents"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        resp = requests.get(endpoint, headers=headers, timeout=30)
        if resp.status_code == 200:
            agents = resp.json()
            if isinstance(agents, dict) and "value" in agents:
                agents = agents["value"]
            
            for agent in agents if isinstance(agents, list) else []:
                if agent.get("name") == agent_name or agent.get("id") == agent_name.lower().replace(" ", "-"):
                    log(f"✓ Agent found: {agent.get('name')} (ID: {agent.get('id')})", "SUCCESS")
                    return agent
            
            log(f"Agent not found in list yet (may take a moment to appear)", "INFO")
            return None
    except Exception as e:
        log(f"Could not verify agent: {str(e)}", "WARNING")
        return None

def main():
    global FUNCTION_KEY, FOUNDRY_PROJECT_URL
    
    import requests
    
    # Check if requests is installed
    try:
        import requests
    except ImportError:
        log("Installing requests library...", "INFO")
        subprocess.run([sys.executable, "-m", "pip", "install", "requests", "-q"], check=True)
        import requests
    
    log("=" * 70, "")
    log("Azure AI Foundry Agent Deployment", "")
    log("=" * 70, "")
    
    # Get parameters from command line or user input
    if len(sys.argv) > 1:
        FUNCTION_KEY = sys.argv[1]
    if len(sys.argv) > 2:
        FOUNDRY_PROJECT_URL = sys.argv[2]
    
    if not FUNCTION_KEY:
        log("Function key not provided", "ERROR")
        sys.exit(1)
    
    if not FOUNDRY_PROJECT_URL:
        FOUNDRY_PROJECT_URL = "https://tagoreautomation-2862-resource.services.ai.azure.com/api/projects/tagoreautomation-2862"
        log(f"Using default Foundry URL: {FOUNDRY_PROJECT_URL}", "INFO")
    
    try:
        # Step 1: Authenticate
        log("", "")
        log("STEP 1: Authentication", "")
        log("-" * 70, "")
        token = get_access_token()
        
        # Step 2: Create agent
        log("", "")
        log("STEP 2: Deploy Agent to Foundry", "")
        log("-" * 70, "")
        result = create_agent_via_api(token, FOUNDRY_PROJECT_URL, FUNCTION_KEY)
        
        # Step 3: Verify
        log("", "")
        log("STEP 3: Verification", "")
        log("-" * 70, "")
        verify_agent_deployment(token, FOUNDRY_PROJECT_URL, AGENT_NAME)
        
        # Summary
        log("", "")
        log("=" * 70, "")
        log("DEPLOYMENT COMPLETE!", "SUCCESS")
        log("=" * 70, "")
        log("", "")
        log(f"Agent Name: {AGENT_NAME}", "INFO")
        log(f"Backend URL: {FUNCTION_ENDPOINT}", "INFO")
        log(f"Foundry Project: {FOUNDRY_PROJECT_URL}", "INFO")
        log("", "")
        log("Next Steps:", "INFO")
        log("1. Open Azure AI Foundry: https://ai.azure.com", "INFO")
        log(f"2. Find your agent: {AGENT_NAME}", "INFO")
        log("3. Go to Test/Playground tab", "INFO")
        log("4. Send a test message:", "INFO")
        log('   {"text": "Vendor: Test Corp\\nInvoice # 123\\nAmount: $500"}', "INFO")
        log("", "")
        
    except Exception as e:
        log("", "")
        log("DEPLOYMENT FAILED", "ERROR")
        log(str(e), "ERROR")
        log("", "")
        log("Troubleshooting:", "ERROR")
        log("1. Ensure you're logged in: az login", "ERROR")
        log("2. Check Azure CLI is installed: az --version", "ERROR")
        log("3. Verify function key is correct", "ERROR")
        log("4. Check Foundry project URL", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()
