# âœ… Your Invoice Agent Deployment - Next Steps

## Status
Your invoice agent **infrastructure is deployed and working**:
- âœ… Azure Function App running with Document Intelligence
- âœ… HTTP endpoint: `https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice`
- âœ… Authentication: Function key configured
- âœ… All code pushed to GitHub

## â³ What's Left: Register Agent in Azure AI Foundry

We encountered terminal issues executing the API deployment script. **Two simple options:**

---

## **Option 1: Manual Registration (Recommended - 5 min)**

1. Go to: https://ai.azure.com
2. Sign in with your Azure account
3. Select Project: `tagoreautomation-2862`
4. Click **Agents** â†’ **Create new agent**
5. Fill in:
   - **Name:** `invoice-agent`
   - **Description:** `Invoice extraction and analysis using Document Intelligence`
6. For **Backend Configuration:**
   - **Type:** HTTP Webhook
   - **URL:** `https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice`
   - **Headers:** Add custom header
     - Name: `x-functions-key`
     - Value: `<AZURE_FUNCTION_KEY>`
7. Click **Save** â†’ **Publish**

---

## **Option 2: Auto-Deploy (Use This Script)**

We created deployment scripts. When the terminal is ready, run:

```bash
# PowerShell
.\deploy_foundry_agent.ps1 -AccessToken "<your_token_here>"

# Or Python
python deploy_foundry_agent.py "<your_token_here>"

# Or Batch
.\deploy_foundry_agent.bat
```

Get a fresh token with:
```bash
az account get-access-token --resource https://ai.azure.com
```

---

## **Testing Your Agent**

Once registered in Foundry, test with:

### Via Foundry UI
1. Open your agent
2. Click **Test** / **Playground**
3. Send:
```json
{
  "text": "Vendor: Acme Corp\nInvoice #2024-001\nDate: 2024-07-12\nAmount: $1,500.00"
}
```

### Via Direct HTTP
```bash
curl -X POST \
  -H "x-functions-key: <AZURE_FUNCTION_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"text":"Vendor: Test\nInvoice #123\nAmount: $500"}' \
  https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice
```

### Via Python
```bash
pip install requests
python scripts/test_foundry_agent.py
```

---

## Expected Response
```json
{
  "extracted_fields": {
    "vendor_name": "Acme Corp",
    "invoice_number": "2024-001",
    "total_amount": 1500.0,
    "invoice_date": "2024-07-12"
  },
  "analysis": {
    "document_type": "Invoice",
    "vendor_name": "Acme Corp",
    "invoice_number": "2024-001",
    "total_amount": 1500.0,
    "invoice_date": "2024-07-12",
    "confidence": 0.95,
    "issues": []
  }
}
```

---

## ðŸ“‹ Quick Checklist

- [ ] Register agent in Foundry (Option 1 or 2)
- [ ] Test in Foundry Playground
- [ ] Verify extracted_fields in response
- [ ] Deploy to production (if needed)

---

**Your function key (for future reference):**
```
<AZURE_FUNCTION_KEY>
```

**All files are ready in:**
- `/foundry/` - Configuration files
- `/scripts/` - Test and deployment scripts
- GitHub: https://github.com/tagauto/classificationagent_azureai.git

ðŸŽ‰ **You're 95% doneâ€”just need to register the agent in the Foundry UI!**

