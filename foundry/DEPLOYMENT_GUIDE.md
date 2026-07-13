# Azure AI Foundry Agent Deployment Guide

**Agent**: invoice-agent  
**Backend Type**: HTTP Webhook (Azure Function App)  
**Status**: Ready for Deployment  
**Created**: 2026-07-12

---

## Quick Start

Your invoice-agent is configured and ready to deploy. Here's how:

### Prerequisites
- Azure subscription access (`d65af6df-c048-43eb-8cfd-ea54c482e516`)
- Azure CLI installed (`az login` completed)
- Azure AI Foundry project set up
- Function App deployed: `https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice`

---

## Agent Configuration Summary

```json
{
  "name": "invoice-agent",
  "description": "Invoice extraction and analysis using Document Intelligence",
  "backend": {
    "type": "http",
    "url": "https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice",
    "auth": {
      "type": "header",
      "headerName": "x-functions-key",
      "headerValue": "[FUNCTION_KEY]"
    }
  },
  "inputSchema": {
    "text": "Invoice text to analyze (required)",
    "file_path": "Path to invoice file (optional)"
  },
  "outputSchema": {
    "extracted_fields": {
      "vendor_name": "string",
      "invoice_number": "string",
      "total_amount": "number",
      "invoice_date": "string"
    },
    "analysis": {
      "document_type": "string",
      "confidence": "number",
      "vendor_name": "string",
      "invoice_number": "string",
      "total_amount": "number",
      "invoice_date": "string",
      "issues": ["array of strings"]
    }
  }
}
```

---

## Deployment Methods

### Option 1: Manual Deployment via Foundry UI (Recommended)

**Easiest approach - no scripting required**

1. **Open Azure AI Foundry**
   - Go to [https://ai.azure.com](https://ai.azure.com)
   - Sign in with your Azure account
   - Select your Foundry project

2. **Create New Agent**
   - Navigate to **Agents** → **+ Create Agent**
   - Choose agent type: **HTTP Trigger** or **Custom HTTP**

3. **Configure Basic Details**
   - **Name**: `invoice-agent`
   - **Description**: `Invoice extraction and analysis using Document Intelligence`

4. **Configure Backend**
   - **Backend Type**: HTTP Webhook
   - **Endpoint URL**: `https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice`

5. **Add Authentication Header**
   - **Header Name**: `x-functions-key`
   - **Header Value**: Get from terminal:
     ```bash
     az functionapp keys list \
       --name invoice-agent-docintelligence2 \
       --resource-group rmtag-openai-agents-rg \
       --query 'functionKeys.default' -o tsv
     ```

6. **Set Input Schema**
   Copy from [./agent_registration.json](./agent_registration.json) - `inputSchema` section

7. **Set Output Schema**
   Copy from [./agent_registration.json](./agent_registration.json) - `outputSchema` section

8. **Review and Publish**
   - Click **Create** to save
   - Click **Publish** to make it available

---

### Option 2: Automated Setup via PowerShell Script

**For CI/CD and automated deployments**

```powershell
# Run the deployment script
.\scripts\deploy_to_foundry.ps1 `
  -FoundryProjectUrl "https://your-resource.services.ai.azure.com/api/projects/your-project"
```

The script will:
- ✓ Validate prerequisites
- ✓ Authenticate with Azure
- ✓ Retrieve function key automatically
- ✓ Display deployment options
- ✓ Provide test commands

---

### Option 3: Deploy via REST API (Advanced)

**For programmatic deployment**

```bash
# Step 1: Get access token
TOKEN=$(az account get-access-token --resource "https://ai.azure.com" --query accessToken -o tsv)

# Step 2: Get function key
FUNC_KEY=$(az functionapp keys list \
  --name invoice-agent-docintelligence2 \
  --resource-group rmtag-openai-agents-rg \
  --query 'functionKeys.default' -o tsv)

# Step 3: Deploy agent (adjust FOUNDRY_PROJECT_ENDPOINT)
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "invoice-agent",
    "description": "Invoice extraction and analysis using Document Intelligence",
    "backend": {
      "type": "http",
      "url": "https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice",
      "auth": {
        "type": "header",
        "headerName": "x-functions-key",
        "headerValue": "'$FUNC_KEY'"
      }
    },
    "inputSchema": {
      "type": "object",
      "properties": {
        "text": {"type": "string", "description": "Invoice text to analyze"},
        "file_path": {"type": "string", "description": "Path to invoice file (optional)"}
      },
      "required": ["text"]
    },
    "outputSchema": {
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
            "issues": {"type": "array", "items": {"type": "string"}}
          }
        }
      }
    }
  }' \
  "https://YOUR_FOUNDRY_PROJECT_URL/agents"
```

Replace `YOUR_FOUNDRY_PROJECT_URL` with your Foundry project endpoint.

---

### Option 4: Deploy via Azure CLI (if supported)

**If your Azure CLI version supports Foundry commands**

```bash
az ai foundry agent create \
  --name invoice-agent \
  --description "Invoice extraction and analysis using Document Intelligence" \
  --backend-type http \
  --backend-url "https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice" \
  --auth-header "x-functions-key: <function-key>" \
  --input-schema @agent_registration.json \
  --output-schema @agent_registration.json
```

---

## Testing the Deployed Agent

### Test 1: Direct HTTP Request

```bash
# Get function key
FUNC_KEY=$(az functionapp keys list \
  --name invoice-agent-docintelligence2 \
  --resource-group rmtag-openai-agents-rg \
  --query 'functionKeys.default' -o tsv)

# Send test request
curl -X POST \
  -H "Content-Type: application/json" \
  -H "x-functions-key: $FUNC_KEY" \
  -d '{
    "text": "Vendor: Northwind Property Services\nInvoice #10042\nDate: 2026-07-10\nAmount Due: $1250.00"
  }' \
  https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice
```

**Expected Response:**
```json
{
  "extracted_fields": {
    "vendor_name": "Northwind Property Services",
    "invoice_number": "10042",
    "total_amount": 1250.00,
    "invoice_date": "2026-07-10"
  },
  "analysis": {
    "document_type": "vendor_invoice",
    "confidence": 0.95,
    "vendor_name": "Northwind Property Services",
    "invoice_number": "10042",
    "total_amount": 1250.00,
    "invoice_date": "2026-07-10",
    "issues": []
  }
}
```

### Test 2: Python Test Script

```bash
python scripts/test_invoke.py
```

### Test 3: Foundry UI Test

1. Open the agent in Foundry
2. Go to **Test** or **Playground**
3. Send a test message:
   ```json
   {
     "text": "Vendor: Acme Corp\nInvoice #2026-001\nDate: 2026-07-12\nAmount: $500.00"
   }
   ```
4. Review response and traces

### Test 4: Monitor Function App Logs

```bash
# Real-time log tail
az webapp log tail \
  --name invoice-agent-docintelligence2 \
  --resource-group rmtag-openai-agents-rg

# Download logs
az webapp log download \
  --name invoice-agent-docintelligence2 \
  --resource-group rmtag-openai-agents-rg \
  --log-file ./logs.zip
```

---

## Important Notes

### Security
- **DO NOT** commit `agent_registration.json` (contains function key) to git
- **DO NOT** share the function key publicly
- Store the key in **Azure Key Vault** for production
- Use managed identities when possible instead of keys

### Function Key Rotation
If you need to rotate the function key:

```bash
# List and view existing keys
az functionapp function keys list \
  --name invoice-agent-docintelligence2 \
  --resource-group rmtag-openai-agents-rg

# Delete old key
az functionapp function key delete \
  --name invoice-agent-docintelligence2 \
  --resource-group rmtag-openai-agents-rg \
  --function-name invoiceprocessor \
  --key-name old_key_name

# Update agent with new key
```

### Monitoring and Alerts
Set up monitoring for your agent:

```bash
# View metrics
az monitor metrics list \
  --resource /subscriptions/d65af6df-c048-43eb-8cfd-ea54c482e516/resourceGroups/rmtag-openai-agents-rg/providers/Microsoft.Web/sites/invoice-agent-docintelligence2 \
  --metric HttpSuccessful4xx \
  --start-time 2026-07-10 \
  --end-time 2026-07-12 \
  --interval PT1H
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Agent not responding** | Check Function App logs: `az webapp log tail ...` |
| **Authentication fails** | Verify function key is current: `az functionapp keys list ...` |
| **Timeout errors** | Check Function App performance and timeout settings |
| **Validation errors** | Ensure input schema matches test payload exactly |
| **Can't get token** | Run `az login` and ensure correct subscription is set |

---

## Files Reference

| File | Purpose |
|------|---------|
| [agent_registration.json](./agent_registration.json) | Complete agent configuration with schemas |
| [agent_registration.json.template](./agent_registration.json.template) | Template for agent registration |
| [AGENT_REGISTRATION.md](./AGENT_REGISTRATION.md) | Original registration instructions |
| [TESTING_AND_REGISTRATION.md](./TESTING_AND_REGISTRATION.md) | Detailed testing guide |

---

## Support

For issues:
1. Check Function App logs: `az webapp log tail --name invoice-agent-docintelligence2 --resource-group rmtag-openai-agents-rg`
2. Verify agent configuration in Foundry UI
3. Test directly: `curl -H "x-functions-key: $KEY" <endpoint>`
4. Check Azure portal for metrics and alerts

---

**Ready to deploy?** Choose your deployment method above and follow the steps!
