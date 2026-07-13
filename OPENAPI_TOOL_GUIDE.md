# Using the Invoice API as a Tool in Azure AI Foundry

## Quick Start

You now have two versions of the OpenAPI schema for your invoice processing function:
- **JSON**: `openapi_schema.json` (for Foundry UI)
- **YAML**: `openapi_schema.yaml` (alternative format)

## How to Add as a Tool in Foundry

### Option 1: Via Foundry UI

1. **Go to**: https://ai.azure.com/projects/tagoreautomation-2862
2. **Navigate to**: "Tools" or "Custom Tools" section
3. **Click**: "+ Add Tool" or "+ New Tool"
4. **Select**: "OpenAPI/REST API"
5. **Choose how to provide schema**:
   - **Option A**: Upload the JSON file
     - Click "Upload"
     - Select `openapi_schema.json`
   - **Option B**: Paste the content
     - Copy entire content from `openapi_schema.json`
     - Paste into the schema field
6. **Configure Authentication**:
   - **Type**: API Key
   - **Header Name**: `x-functions-key`
   - **Header Value**: `<AZURE_FUNCTION_KEY>`
7. **Review** the detected operations (should show `processInvoice`)
8. **Click**: "Create Tool" or "Save"

### Option 2: Via Python SDK (When Fixed)

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
import json

# Load the schema
with open("openapi_schema.json", "r") as f:
    openapi_spec = json.load(f)

# Connect to Foundry
client = AIProjectClient(
    endpoint="https://tagoreautomation-2862-resource.services.ai.azure.com",
    credential=DefaultAzureCredential()
)

# Create OpenAPI tool (once SDK methods are fixed)
# tool = client.tools.create_openapi_tool(
#     name="invoice_processor",
#     schema=json.dumps(openapi_spec),
#     auth={"type": "header", "name": "x-functions-key", "value": "KEY"}
# )
```

---

## Schema Overview

### Endpoint
- **URL**: `https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice`
- **Method**: `POST`
- **Auth**: Header `x-functions-key`

### Input Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `text` | string | Yes | Invoice text content to analyze |
| `file_path` | string | No | Path to invoice file (alternative to text) |

### Output Response

```json
{
  "extracted_fields": {
    "vendor_name": "Acme Corporation",
    "invoice_number": "INV-2024-001",
    "total_amount": 1500.00,
    "invoice_date": "2024-07-10"
  },
  "analysis": {
    "document_type": "vendor_invoice",
    "confidence": 0.95,
    "vendor_name": "Acme Corporation",
    "invoice_number": "INV-2024-001",
    "total_amount": 1500.00,
    "invoice_date": "2024-07-10",
    "issues": []
  }
}
```

---

## Example Usage in Foundry Agent

Once the tool is registered, your agent can use it like:

```
User: "Process this invoice for me: Vendor Acme, Invoice #001, Date: 2024-07-10, Amount: $1500"

Agent: [Calls processInvoice tool]
â†’ Extracts: vendor_name, invoice_number, total_amount, invoice_date
â†’ Returns confidence score and document classification
â†’ Presents structured data to user
```

---

## Validation

### Test the Endpoint Directly

```bash
# Test with invoice text
curl -X POST https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice \
  -H "x-functions-key: <AZURE_FUNCTION_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Invoice #INV-2024-001\nVendor: Acme Corporation\nDate: 2024-07-10\nTotal: $1,500.00"
  }'
```

### Expected Response (200 OK)

```json
{
  "extracted_fields": {
    "vendor_name": "Acme Corporation",
    "invoice_number": "INV-2024-001",
    "total_amount": 1500.0,
    "invoice_date": "2024-07-10"
  },
  "analysis": {
    "document_type": "vendor_invoice",
    "confidence": 0.95,
    "vendor_name": "Acme Corporation",
    "invoice_number": "INV-2024-001",
    "total_amount": 1500.0,
    "invoice_date": "2024-07-10",
    "issues": []
  }
}
```

---

## Troubleshooting

### Issue: "Authentication failed"
- **Check**: API key value is correct in Foundry tool config
- **Verify**: Header name is exactly `x-functions-key` (case-sensitive)

### Issue: "Invalid OpenAPI schema"
- **Check**: Schema is valid JSON (use `jsonlint`)
- **Verify**: `openapi` field is `3.0.3` or higher
- **Ensure**: `paths` and `components` are properly formatted

### Issue: "Endpoint not reachable"
- **Verify**: Azure Function App is running (check in Azure Portal)
- **Check**: Function key is valid and not expired
- **Test**: Manually curl the endpoint first

---

## Files Generated

- `openapi_schema.json` - JSON format (preferred for Foundry UI)
- `openapi_schema.yaml` - YAML format (alternative)
- `OPENAPI_TOOL_GUIDE.md` - This file

---

## Next Steps

1. âœ… Upload `openapi_schema.json` to Foundry UI
2. âœ… Test tool invocation in agent
3. âœ… Deploy agent with tool registered
4. âœ… Run agent end-to-end test

All set! Your invoice processing function is now ready to be used as a tool in Azure AI Foundry.

