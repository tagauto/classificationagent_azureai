# ðŸš€ Invoice Agent Deployment - Quick Reference

## âš¡ TL;DR - Deploy in 5 Minutes

### **Method 1: UI (Easiest)**
1. Go to https://ai.azure.com â†’ Agents â†’ + Create Agent
2. Name: `invoice-agent`
3. Backend Type: HTTP Webhook
4. URL: `https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice`
5. Auth Header: `x-functions-key: <AZURE_FUNCTION_KEY>`
6. Input Schema: `{"type": "object", "properties": {"text": {"type": "string"}}}`
7. Output Schema: (Copy from agent_registration.json)
8. Click Save â†’ Publish

---

## ðŸ”‘ Key Information

| Item | Value |
|------|-------|
| **Agent Name** | invoice-agent |
| **Backend URL** | https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice |
| **Auth Header** | x-functions-key |
| **Auth Value** | <AZURE_FUNCTION_KEY> |
| **Resource Group** | rmtag-openai-agents-rg |
| **Function App** | invoice-agent-docintelligence2 |
| **Subscription** | d65af6df-c048-43eb-8cfd-ea54c482e516 |

---

## ðŸ“‹ Input Schema

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
  },
  "required": ["text"]
}
```

---

## ðŸ“¤ Output Schema

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

---

## ðŸ§ª Quick Test

```bash
# Test directly
curl -X POST \
  -H "x-functions-key: <AZURE_FUNCTION_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"text": "Vendor: Acme\nInvoice: 123\nAmount: $100"}' \
  https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice

# Or use Python test
python scripts/test_foundry_agent.py
```

---

## âœ… Checklist

- [ ] Azure subscription access
- [ ] Function App is running
- [ ] Foundry project created
- [ ] Choose deployment method
- [ ] Deploy agent
- [ ] Test with sample invoice
- [ ] Monitor logs

---

## ðŸ”— Important URLs

- **Foundry UI**: https://ai.azure.com
- **Azure Portal**: https://portal.azure.com
- **Function App**: https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice
- **Documentation**: See `foundry/DEPLOYMENT_GUIDE.md`

---

## ðŸ“ž Help

| Issue | Solution |
|-------|----------|
| Agent not working | Check Function App logs: `az webapp log tail --name invoice-agent-docintelligence2 --resource-group rmtag-openai-agents-rg` |
| Need new key | `az functionapp keys list --name invoice-agent-docintelligence2 --resource-group rmtag-openai-agents-rg` |
| Function not running | `az functionapp start --name invoice-agent-docintelligence2 --resource-group rmtag-openai-agents-rg` |

---

## ðŸŽ¯ Success Indicators

âœ… Agent shows in Foundry UI  
âœ… Can send test message  
âœ… Receives valid JSON response  
âœ… Extracted fields populated  
âœ… Confidence score > 0  

**You're done when all tests pass!** ðŸŽ‰

---

See `DEPLOYMENT_GUIDE.md` for detailed instructions.

