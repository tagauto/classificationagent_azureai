# Azure AI Foundry Agent Registration & Testing Guide

## Status Summary
✅ Code Deployed: Function App live at `https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice`
✅ Code Committed: Pushed to `https://github.com/tagauto/classificationagent_azureai.git`
✅ Document Intelligence: Configured with credentials

## Function App Details
- **URL**: `https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice`
- **Resource Group**: `rmtag-openai-agents-rg`
- **Region**: East US
- **Function Name**: `invoiceprocessor`
- **HTTP Method**: POST
- **Authentication**: Function-level key (required in header)

## Agent Registration: Option A (Manual Portal Steps)

### 1. Access Azure AI Foundry
1. Open [Azure AI Studio](https://ai.azure.com) or your Foundry workspace URL
2. Select your project (or create one if needed)

### 2. Create Agent
1. Go to **Agents** → **+ New agent**
2. Configure:
   - **Name**: `invoice-agent`
   - **Description**: `Invoice extraction and analysis using Document Intelligence`
   - **Backend Type**: Choose one:
     - **HTTP Trigger / Custom HTTP** (recommended)
     - **Webhook** (if available)
     - **Azure Function** (if direct integration supported)

### 3. Configure HTTP Backend
If using HTTP/Webhook:
1. **Endpoint URL**: `https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice`
2. **Authentication Header**:
   ```
   x-functions-key: <YOUR_FUNCTION_KEY>
   ```
   Get the key with:
   ```bash
   az functionapp function keys list \
     --name invoice-agent-docintelligence2 \
     --resource-group rmtag-openai-agents-rg \
     --function-name invoiceprocessor \
     -o tsv --query default
   ```

3. **Input Schema** (JSON):
   ```json
   {
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
   ```

4. **Output Schema** (JSON):
   ```json
   {
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
   ```

### 4. Save & Publish
- Click **Create** or **Save**
- Review and publish the agent

## Agent Registration: Option B (API/REST)

### Using Azure REST API
Replace placeholders and run:

```bash
# Get authentication token
TOKEN=$(az account get-access-token --query accessToken -o tsv)

# Register agent (example payload - adjust based on your Foundry API)
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "invoice-agent",
    "description": "Invoice extraction and analysis",
    "backend": {
      "type": "http",
      "url": "https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice",
      "auth": {
        "type": "header",
        "headerName": "x-functions-key",
        "headerValue": "<FUNCTION_KEY>"
      }
    }
  }' \
  https://your-foundry-project-url/agents
```

Note: Replace `your-foundry-project-url` with your Foundry project endpoint.

## Testing the Agent: Step-by-Step

### Step 1: Verify Function Health
```bash
# Get function app status
az functionapp show \
  --name invoice-agent-docintelligence2 \
  --resource-group rmtag-openai-agents-rg \
  --query "state" -o tsv
# Should output: "Running"
```

### Step 2: Test with curl (Direct)
```bash
# Get function key
FUNC_KEY=$(az functionapp function keys list \
  --name invoice-agent-docintelligence2 \
  --resource-group rmtag-openai-agents-rg \
  --function-name invoiceprocessor \
  -o tsv --query default)

# Test with sample payload
curl -X POST \
  -H "Content-Type: application/json" \
  -H "x-functions-key: $FUNC_KEY" \
  -d '{
    "text": "Vendor: Northwind Property Services\nInvoice # 10042\nDate: 2026-07-10\nAmount Due: $1250.00"
  }' \
  https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice
```

### Step 3: Test from Foundry UI
1. Open your agent in Foundry
2. Go to **Test** or **Playground**
3. Send a test message:
   ```json
   {
     "text": "Vendor: Acme Corp\nInvoice # 2026-001\nDate: 2026-07-12\nAmount Due: $500.00"
   }
   ```
4. Review the response and logs

### Step 4: Monitor Function App Logs
```bash
# Real-time log tail (5 minutes)
az webapp log tail \
  --name invoice-agent-docintelligence2 \
  --resource-group rmtag-openai-agents-rg

# Or download recent logs
az webapp log download \
  --name invoice-agent-docintelligence2 \
  --resource-group rmtag-openai-agents-rg \
  --log-file ./function-logs.zip
```

### Step 5: Test File Upload (if using Document Intelligence)
```bash
# Example: analyze an invoice file
curl -X POST \
  -H "Content-Type: application/json" \
  -H "x-functions-key: $FUNC_KEY" \
  -d '{
    "file_path": "/samples/sample_invoice.txt"
  }' \
  https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice
```

## Automated Testing

### Python Test Script
```bash
pip install requests
python scripts/test_invoke.py
```

### PowerShell Test Script
```powershell
powershell -ExecutionPolicy Bypass -File scripts/test_invoke.ps1
```

## Production Checklist

- [ ] Verify Document Intelligence endpoint is accessible
- [ ] Verify function key is stored securely (Key Vault recommended)
- [ ] Enable Application Insights monitoring
- [ ] Configure auto-scaling for Flex Consumption plan
- [ ] Add alert thresholds for errors/latency
- [ ] Test end-to-end with various invoice formats
- [ ] Add CI/CD pipeline for automatic function updates
- [ ] Secure the function key in Foundry using managed identity or Key Vault

## Troubleshooting

### Function returns 500 error
1. Check logs: `az webapp log tail --name invoice-agent-docintelligence2 --resource-group rmtag-openai-agents-rg`
2. Verify Document Intelligence credentials
3. Ensure `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT` and `AZURE_DOCUMENT_INTELLIGENCE_KEY` are set

### Authentication fails
1. Verify function key: `az functionapp function keys list --name invoice-agent-docintelligence2 --resource-group rmtag-openai-agents-rg --function-name invoiceprocessor`
2. Confirm header is `x-functions-key` (case-sensitive in some APIs)

### Agent doesn't call the function
1. Verify HTTP backend URL in Foundry is correct
2. Check Foundry logs for outbound call attempts
3. Ensure firewall/NSG allows outbound HTTPS to Azure

## Next Steps
1. Register the agent using Option A or B above
2. Run the test steps above
3. Monitor logs and performance
4. Add CI/CD for automatic deployments
5. Set up alerts and monitoring in Application Insights
