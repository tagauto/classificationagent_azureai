# Deployment example

Use the following commands from the project root once you have Azure CLI and Azure Developer CLI installed.

```bash
az login
az account set --subscription <subscription-id>
azd auth login
azd env new invoice-agent-foundry
azd env set AZURE_LOCATION <azure-region>
azd up
```

After deployment, set these Function App settings in the Azure portal or with Azure CLI:

```bash
az functionapp config appsettings set --settings AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://<resource>.cognitiveservices.azure.com/ AZURE_DOCUMENT_INTELLIGENCE_KEY=<key> --name <function-app-name> --resource-group <resource-group>
```
