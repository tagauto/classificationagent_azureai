# Invoice extraction and classification agent for Azure AI Foundry

This project provides a starter agent for processing vendor invoices submitted to a real estate company. It can:

- extract basic invoice fields from text
- classify a document as a vendor invoice or unknown document
- serve as a local prototype before integrating with Azure AI Document Intelligence and Azure AI Foundry

## Structure

- src/invoice_agent/agent.py: core extraction/classification logic
- tests/test_agent.py: regression tests for the expected behavior

## Run locally

```bash
python -m pip install -e .
pytest -q
invoice-agent "Vendor: Northwind Property Services\nInvoice # 10042\nDate: 2026-07-10\nAmount Due: $1250.00"
```

## Azure AI Document Intelligence

Copy the sample environment template and fill in your values:

```bash
copy .env.example .env
```

Then edit .env and set:

```bash
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://<your-resource>.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=<your-key>
```

Then run:

```bash
invoice-agent C:\path\to\invoice.pdf
```

For a quick local text check, run:

```bash
invoice-agent samples/sample_invoice.txt
```

## Azure Function endpoint

You can also expose the agent over HTTP with Azure Functions.

Install the local host dependencies:

```bash
pip install -r requirements.txt
```

Run the Function App locally:

```bash
func start
```

Then send a request such as:

```bash
curl -X POST http://localhost:7071/api/invoice -H "Content-Type: application/json" -d @samples/sample_request.json
```

For a deployed Function App, use the same payload shape with the deployed URL and the sample request file:

```bash
curl -X POST https://<function-app-name>.azurewebsites.net/api/invoice -H "Content-Type: application/json" -d @samples/sample_deployed_request.json
```

## Deploy to Azure

Provision and deploy the Function App with Azure Developer CLI:

```bash
azd auth login
azd up
```

This uses the Bicep template in the infra folder to create the Function App resources.

If an Azure Developer CLI environment named `invoice-agent-foundry` already exists, the helper scripts will reuse it instead of failing with "environment already exists".
If a resource group already exists in a different location, the scripts will prompt you to either use the existing group location or create a new resource group.

A concrete deployment walkthrough is available in deployment_example.md and a filled example is in deployment_example_filled.md.

You can also run the full deployment flow with the helper scripts:

```bash
bash deploy_commands.sh <subscription-id> <resource-group> <location> <azd-env-name> <function-app-name> <document-intelligence-endpoint> <document-intelligence-key>
```

or on PowerShell:

```powershell
./deploy_commands.ps1 -SubscriptionId <subscription-id> -ResourceGroup <resource-group> -Location <location> -AzdEnvName <azd-env-name> -FunctionAppName <function-app-name> -DocIntelligenceEndpoint <document-intelligence-endpoint> -DocIntelligenceKey <document-intelligence-key>
```

For local development, fill in the values in local.settings.json before running func start.

For GitHub Actions deployment, add these repository secrets:

- AZURE_CREDENTIALS
- AZURE_FUNCTIONAPP_NAME

A sample JSON payload is available in AZURE_CREDENTIALS.example.json.

To create a service principal, run one of the helper scripts:

```bash
bash scripts/create_sp.sh <subscription-id> <resource-group> [service-principal-name]
```

or on PowerShell:

```powershell
./scripts/create_sp.ps1 -SubscriptionId <subscription-id> -ResourceGroup <resource-group> -ServicePrincipalName invoice-agent-foundry
```

If you already know the subscription ID, you can print a GitHub Actions secret template with:

```bash
python scripts/print_github_secret.py <subscription-id>
```

After deployment, set these application settings in the Function App:

- AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT
- AZURE_DOCUMENT_INTELLIGENCE_KEY

## Azure AI Foundry integration next steps

1. Create a Foundry project and connect the agent to Azure AI Document Intelligence.
2. Replace the simple heuristic logic with a hosted model or prompt-based workflow.
3. Add a REST endpoint or Azure Function to receive uploaded invoices and return structured JSON.
4. Store extracted fields in Dataverse, Cosmos DB, or Azure SQL for downstream AP processing.
