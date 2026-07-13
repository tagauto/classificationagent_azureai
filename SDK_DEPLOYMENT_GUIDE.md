# SDK-Based Agent Deployment Guide

## Overview
This guide provides a complete step-by-step process to build and deploy the invoice agent to Azure AI Foundry using the Python SDK (`azure-ai-projects`).

---

## Prerequisites

âœ… **Environment**
- Python 3.9+
- Azure CLI installed and authenticated
- Required packages: `azure-ai-projects`, `azure-identity`

âœ… **Configuration**
- Foundry endpoint: `https://tagoreautomation-2862-resource.services.ai.azure.com`
- Project: `tagoreautomation-2862`
- Subscription: `d65af6df-c048-43eb-8cfd-ea54c482e516`
- Function endpoint: `https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice`
- Function key: `<AZURE_FUNCTION_KEY>`

âœ… **Files Ready**
- `agent_manifest.yaml` - Agent definition
- `openapi_schema.json` - Tool specification
- `agent_deployment_config.json` - Complete configuration

---

## Step 1: Install Dependencies

```bash
pip install azure-ai-projects azure-identity pyyaml requests
```

---

## Step 2: Authentication Setup

Ensure Azure CLI is configured with the correct credentials:

```bash
# Check current subscription
az account show

# Set correct subscription if needed
az account set --subscription d65af6df-c048-43eb-8cfd-ea54c482e516

# Get access token for Foundry
$token = az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv
```

---

## Step 3: Create Agent Using SDK

### Method 1: Using AIProjectClient (Recommended)

```python
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import OpenApiTool, OpenApiAnonymousAuthDetails
import json

# Initialize client
client = AIProjectClient(
    endpoint="https://tagoreautomation-2862-resource.services.ai.azure.com",
    credential=DefaultAzureCredential()
)

# Load OpenAPI schema
with open("openapi_schema.json", "r") as f:
    spec = json.load(f)

# Create OpenAPI tool
tool = OpenApiTool()
tool['spec'] = json.dumps(spec)
tool['description'] = "Invoice processor using Azure Document Intelligence"
tool['auth'] = OpenApiAnonymousAuthDetails()

# Create agent
agent = client.agents.create_agent(
    name="invoice-agent",
    model="gpt-4o-mini",
    instructions="""You are an intelligent invoice processing assistant powered by Azure Document Intelligence.
Your role is to help users process and analyze invoice documents.

When a user provides invoice text or asks you to process an invoice:
1. Use the invoice_processor tool to extract structured data
2. Present the extracted information clearly
3. Highlight the confidence score of the extraction
4. Note any issues or warnings from the analysis
5. Provide a summary of key invoice details""",
    tools=[tool]
)

print(f"Agent created: {agent.id}")
```

### Method 2: Using Manifest File

```python
import yaml
from azure.ai.projects import AIProjectClient

# Load manifest
with open("agent_manifest.yaml", "r") as f:
    manifest = yaml.safe_load(f)

# Create agent from manifest
agent = client.agents.create_version_from_manifest(
    name=manifest['name'],
    manifest=manifest
)

print(f"Agent deployed: {agent['id']}")
```

---

## Step 4: Register OpenAPI Tool

Once the agent is created, register the invoice processing tool:

```python
# The tool is already included in the agent creation above
# But if adding later:

tool_registration = {
    "type": "openapi",
    "name": "invoice_processor",
    "spec": spec,
    "auth": {
        "type": "header",
        "header_name": "x-functions-key",
        "header_value": "<AZURE_FUNCTION_KEY>"
    }
}

# Update agent with tool
agent = client.agents.update_agent(
    agent_id=agent.id,
    tools=[tool_registration]
)
```

---

## Step 5: Test Agent Locally

```python
# Create a test session
session = client.agents.create_session(agent_id=agent.id)

# Send a test message
response = client.agents.invoke(
    agent_id=agent.id,
    session_id=session.id,
    user_message="Process this invoice: Invoice #001, Vendor: Acme Corp, Amount: $500"
)

print(f"Agent response: {response}")
```

---

## Step 6: Verify Deployment

Check agent status and details:

```python
# Get agent details
agent_details = client.agents.get(agent_id=agent.id)
print(f"Agent Status: {agent_details}")

# List all agents
all_agents = client.agents.list()
for a in all_agents:
    print(f"- {a['name']} (ID: {a['id']})")
```

---

## Step 7: Access in Foundry UI

Once deployed, access your agent:

1. Go to: `https://ai.azure.com/projects/tagoreautomation-2862`
2. Navigate to **Agents** section
3. Find **invoice-agent**
4. Click to open and test in Playground

---

## Alternative: Using REST API

If SDK methods are unavailable, use REST API directly:

```bash
# Create agent via REST API
curl -X POST \
  https://tagoreautomation-2862-resource.services.ai.azure.com/api/agents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @agent_deployment_config.json
```

---

## Troubleshooting

### Issue: `Method not found` error
- SDK may be under development
- Solution: Use REST API or manual Foundry UI creation
- Verify SDK version: `pip show azure-ai-projects`

### Issue: Authentication error (401)
- Token may have expired
- Solution: Regenerate: `az account get-access-token --resource https://ai.azure.com`

### Issue: Tool not working
- Verify OpenAPI spec is valid: `jsonschema validate openapi_schema.json`
- Check function endpoint is accessible
- Verify function key is correct

### Issue: Agent not visible in UI
- Wait 30 seconds for propagation
- Refresh page
- Check Foundry project settings

---

## Next Steps

1. **Test in Foundry Playground** - Send sample invoices
2. **Monitor execution** - Check logs and traces
3. **Iterate** - Refine instructions and tool configuration as needed
4. **Deploy to production** - Publish for end users

---

## Files Reference

| File | Purpose |
|------|---------|
| `agent_manifest.yaml` | Agent definition (name, model, instructions, tools) |
| `openapi_schema.json` | OpenAPI 3.0.3 specification for invoice endpoint |
| `agent_deployment_config.json` | Complete deployment configuration |
| `build_and_deploy_agent.py` | Automated deployment script |
| `AGENT_BUILD_PLAN.md` | Phase-by-phase deployment plan |

---

## Support

For more details:
- Azure AI Foundry: https://ai.azure.com
- Python SDK docs: https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects
- Invoice function: https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice


