# Deployment example (filled for a typical setup)

Replace the placeholder values below with your own subscription, resource group, region, and Function App name.

```bash
az login
az account set --subscription 00000000-0000-0000-0000-000000000000
azd auth login
azd env new invoice-agent-foundry
azd env set AZURE_LOCATION eastus
azd up
```

After deployment, set the Function App settings:

```bash
az functionapp config appsettings set \
  --settings \
  AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://<your-resource>.cognitiveservices.azure.com/ \
  AZURE_DOCUMENT_INTELLIGENCE_KEY=<your-key> \
  --name invoice-agent-foundry-func \
  --resource-group invoice-agent-rg
```
