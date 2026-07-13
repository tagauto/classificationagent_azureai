# Invoice Agent - Complete Deployment Guide

## Executive Summary

âœ… **Status:** Agent is **ready for deployment** to Azure AI Foundry  
âœ… **Files:** All configuration files prepared and validated  
âœ… **Integration:** OpenAPI tool configured with function endpoint  
âœ… **Authentication:** Complete with Foundry credentials  
âœ… **Next Action:** Execute deployment command (choose one option below)

---

## What We've Built

### Agent Configuration
- **Name:** `invoice-agent`
- **Model:** `gpt-4o-mini`
- **Type:** HTTP webhook with OpenAPI tool integration
- **Backend:** Azure Function (`/api/invoice` endpoint)
- **Purpose:** Extract and analyze invoice documents using Azure Document Intelligence

### Integrated Tool
- **Type:** OpenAPI 3.0.3
- **Function:** Invoice processor
- **Endpoint:** `https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice`
- **Authentication:** API key via `x-functions-key` header
- **Capabilities:** Extract vendor name, invoice number, amount, date with confidence scores

### Infrastructure
- **Foundry Project:** `tagoreautomation-2862` (West US)
- **Foundry Endpoint:** `https://tagoreautomation-2862-resource.services.ai.azure.com`
- **Subscription:** `d65af6df-c048-43eb-8cfd-ea54c482e516`
- **Resource Group:** `rmtag-openai-agents-rg`
- **Function App:** `invoice-agent-docintelligence2` (Flex Consumption)

---

## Deployment Options (Choose One)

### ðŸŽ¯ Option 1: REST API (Recommended - Most Reliable)

**Best for:** Production deployments, CI/CD automation

**Command:**
```bash
python deploy_agent_rest_api.py
```

**What it does:**
1. Authenticates with Azure CLI
2. Gets access token for Foundry
3. Sends POST request to create agent
4. Verifies deployment
5. Generates deployment report

**Files:**
- Script: `deploy_agent_rest_api.py`
- Logs: `agent_deployment_*.log`
- Result: `DEPLOYMENT_SUCCESS.md`

**Status:** âœ… Ready to execute

---

### ðŸ”· Option 2: Azure AI Foundry SDK

**Best for:** Programmatic control, Python-native applications

**Script Location:** `build_and_deploy_agent.py`

**Prerequisites:**
```bash
pip install azure-ai-projects azure-identity
```

**Method:**
```python
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

client = AIProjectClient(
    endpoint="https://tagoreautomation-2862-resource.services.ai.azure.com",
    credential=DefaultAzureCredential()
)

agent = client.agents.create_agent(
    name="invoice-agent",
    model="gpt-4o-mini",
    instructions="..."  # See agent_manifest.yaml
)
```

**Status:** âš ï¸ SDK incomplete (method gaps noted in session history)  
**Alternative:** Use REST API option instead

---

### ðŸŒ Option 3: Manual UI Deployment

**Best for:** First-time setup, visual verification

**Steps:**
1. Go to: https://ai.azure.com/projects/tagoreautomation-2862
2. Click "Create Agent" or "Create New"
3. **Agent Settings:**
   - Name: `invoice-agent`
   - Model: `gpt-4o-mini`
   - Description: "Invoice extraction and analysis using Document Intelligence"
4. **Instructions:** Paste from `agent_manifest.yaml`
5. **Add Tool:**
   - Type: OpenAPI
   - Upload: `openapi_schema.json`
   - Or paste spec from file
6. **Configure Authentication:**
   - Header: `x-functions-key`
   - Value: `<AZURE_FUNCTION_KEY>`
7. **Save & Deploy**

**Reference:** See `OPENAPI_TOOL_GUIDE.md` for detailed UI steps

**Status:** âœ… Verified working (from previous sessions)

---

## Configuration Files Reference

| File | Purpose | Status |
|------|---------|--------|
| `agent_manifest.yaml` | Agent definition (model, instructions, tools) | âœ… Ready |
| `openapi_schema.json` | OpenAPI 3.0.3 tool specification | âœ… Valid |
| `openapi_schema.yaml` | YAML variant of schema | âœ… Valid |
| `agent_deployment_config.json` | Complete deployment config | âœ… Ready |
| `deploy_agent_rest_api.py` | REST API deployment script | âœ… Ready |
| `build_and_deploy_agent.py` | SDK deployment script | âš ï¸ Needs SDK |
| `SDK_DEPLOYMENT_GUIDE.md` | Detailed SDK guide | âœ… Reference |
| `AGENT_BUILD_PLAN.md` | Phase-by-phase plan | âœ… Reference |
| `OPENAPI_TOOL_GUIDE.md` | Manual UI deployment guide | âœ… Reference |

---

## ðŸš€ QUICK START: Deploy Now

### Method 1: Automated (Recommended)

```bash
# Prerequisites: Azure CLI installed and authenticated
# Run from: c:\Code\invoice_agent_foundry

python deploy_agent_rest_api.py
```

**Expected Output:**
```
======================================================================
  INVOICE AGENT DEPLOYMENT TO AZURE AI FOUNDRY
======================================================================

[Step 1/5] Obtaining Azure Access Token
âœ“ Token obtained successfully

[Step 2/5] Preparing Agent Configuration
âœ“ Agent name: invoice-agent
âœ“ Model: gpt-4o-mini
âœ“ Tools: 1 configured

[Step 3/5] Deploying Agent to Azure AI Foundry
âœ“ Status: 200 OK
âœ“ Agent created successfully!
âœ“ Agent ID: invoice-agent-xxx

[Step 4/5] Verifying Deployment
âœ“ Agent found: invoice-agent
âœ“ Status: active

[Step 5/5] Generating Summary
âœ“ Summary saved: DEPLOYMENT_SUCCESS.md

âœ… Agent successfully deployed!
URL: https://ai.azure.com/projects/tagoreautomation-2862/agents/invoice-agent-xxx
```

### Method 2: Manual (5 minutes)

See Option 3 above - use Foundry UI at https://ai.azure.com

---

## Testing After Deployment

### Via Foundry Playground

1. Open agent URL from deployment output
2. Click "Playground" or "Test" tab
3. Send message: `"Process: Invoice #001, Vendor: Acme, Amount: $500"`
4. Verify agent calls the invoice processor tool
5. Check extracted fields and confidence score

### Via REST API

```bash
# Get access token
$token = az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv

# Call agent (adjust agent-id from deployment output)
curl -X POST `
  https://tagoreautomation-2862-resource.services.ai.azure.com/agents/invoice-agent/invoke `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d '{"message": "Process invoice: Vendor Acme, Invoice #001, Amount $500"}'
```

### Via Python

```python
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

client = AIProjectClient(
    endpoint="https://tagoreautomation-2862-resource.services.ai.azure.com",
    credential=DefaultAzureCredential()
)

# Invoke agent
session = client.agents.create_session(agent_id="invoice-agent")
response = client.agents.invoke(
    agent_id="invoice-agent",
    session_id=session.id,
    user_message="Process: Invoice #INV-001, Vendor: Acme Corp, Total: $1500"
)

print(response)
```

---

## Deployment Checklist

- [ ] Azure CLI installed: `az --version`
- [ ] Azure CLI authenticated: `az account show`
- [ ] Correct subscription: `az account set --subscription d65af6df-c048-43eb-8cfd-ea54c482e516`
- [ ] Python 3.9+: `python --version`
- [ ] Foundry files ready (manifest, schema, config)
- [ ] Function endpoint accessible: `curl https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice`
- [ ] Run deployment: `python deploy_agent_rest_api.py`
- [ ] Verify in Foundry UI: https://ai.azure.com/projects/tagoreautomation-2862
- [ ] Test in Playground
- [ ] Monitor logs and execution

---

## Troubleshooting

### Common Issues

#### âŒ "Authentication failed" / 401 Error
**Solution:**
```bash
# Regenerate token with correct audience
az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv

# Verify correct subscription
az account show --query id
```

#### âŒ "API version not supported"
**Solution:**
- Script uses `2024-12-01-preview` API version
- If fails, try different version in deployment script
- Check REST API reference: https://learn.microsoft.com/en-us/azure/ai-services/agents/

#### âŒ "Function endpoint not accessible"
**Solution:**
```bash
# Test function directly
curl -X POST https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice \
  -H "x-functions-key: <AZURE_FUNCTION_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"text": "Invoice #001, Vendor: Acme, Amount: $500"}'

# Should return 200 with extracted fields
```

#### âŒ "Agent not visible in UI after deployment"
**Solution:**
- Wait 30 seconds for propagation
- Refresh page
- Check project settings
- Verify agent was created (check deployment logs)

---

## What Happens During Deployment

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ 1. Get Access Token                     â”‚
â”‚    (Azure CLI â†’ Foundry resource)       â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
              â†“
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ 2. Prepare Configuration                â”‚
â”‚    (Load manifest, schema, config)      â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
              â†“
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ 3. Send POST Request to Foundry API     â”‚
â”‚    (Create agent with HTTP webhook)     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
              â†“
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ 4. Receive Agent ID                     â”‚
â”‚    (Confirm creation)                   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
              â†“
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ 5. Verify Agent                         â”‚
â”‚    (Confirm it's accessible)            â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
              â†“
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ 6. Agent Ready in Foundry               â”‚
â”‚    (Accessible via UI & API)            â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## After Deployment

### Immediate Actions
- [ ] Test in Foundry Playground
- [ ] Verify tool invocations work
- [ ] Check extracted field accuracy
- [ ] Monitor confidence scores

### Configuration Updates
If you need to modify the agent after deployment:

```bash
# Option 1: Edit in Foundry UI
# Go to agent details and modify settings

# Option 2: Via REST API (requires PATCH/PUT)
# Similar to deployment script but with UPDATE operation

# Option 3: Delete and redeploy
# Run deployment script again (will update existing agent)
```

### Production Readiness
- [ ] Enable monitoring and alerts
- [ ] Set up logging for all invocations
- [ ] Test with realistic invoice samples
- [ ] Document API contracts for consumers
- [ ] Set up feedback loop for continuous improvement

---

## Reference Documentation

| Document | Purpose |
|----------|---------|
| `SDK_DEPLOYMENT_GUIDE.md` | Detailed SDK usage patterns |
| `AGENT_BUILD_PLAN.md` | Phase-by-phase deployment plan |
| `OPENAPI_TOOL_GUIDE.md` | Manual UI deployment steps |
| `agent_manifest.yaml` | Agent definition |
| `openapi_schema.json` | Tool OpenAPI specification |

---

## Support & Escalation

### Resources
- ðŸ“š Azure AI Foundry: https://ai.azure.com
- ðŸ“– Python SDK: https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects
- ðŸ” Function App: https://portal.azure.com
- ðŸ“ Logs: `agent_deployment_*.log`

### Common Questions

**Q: Can I update the agent after deployment?**  
A: Yes, via Foundry UI or by running the deployment script again (it updates existing agents)

**Q: How do I add more tools?**  
A: Update `agent_manifest.yaml`, add to `tools[]` section, redeploy

**Q: Can I use a different model?**  
A: Yes, change `model: gpt-4o-mini` to preferred model in manifest

**Q: How do I monitor usage?**  
A: Check Foundry project dashboard and Function App metrics

---

## ðŸŽ‰ You're Ready!

All files are prepared and validated. Choose your deployment method above and execute:

```bash
python deploy_agent_rest_api.py
```

**Expected time:** 2-5 minutes  
**Success indicator:** Agent appears in https://ai.azure.com/projects/tagoreautomation-2862

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-15  
**Status:** âœ… READY FOR DEPLOYMENT


