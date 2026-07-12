Agent registration instructions for Azure AI Foundry

This folder contains a manifest and instructions to register the `invoice-agent` as an HTTP-backed agent in Azure AI Foundry (Azure AI Studio / Foundry).

1. Prepare values
   - FUNCTION_URL: https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice
   - FUNCTION_KEY: <your-function-key> (do not check secrets into source control)

2. Manual portal steps
   - Open Azure AI Studio (Foundry) in the Azure portal or standalone AI Studio URL.
   - Go to **Agents** → **Create agent**.
   - Choose a name, e.g., `invoice-agent`.
   - For backend, choose HTTP Webhook (or Custom HTTP) and enter the `FUNCTION_URL`.
   - If the Foundry UI supports custom headers, add header `x-functions-key: <FUNCTION_KEY>`.
     Otherwise append `?code=<FUNCTION_KEY>` to the URL.
   - Save and publish the agent.

3. Example registration payload (if using API to register)
   - Replace placeholders before use; do NOT store secrets in the repo.

File: agent_registration.json.template

```json
{
  "name": "invoice-agent",
  "description": "Invoice extraction agent using Document Intelligence",
  "backend": {
    "type": "http",
    "url": "https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice",
    "auth": {
      "type": "header",
      "headerName": "x-functions-key",
      "headerValue": "<FUNCTION_KEY>"
    }
  },
  "inputSchema": {
    "type": "object",
    "properties": {
      "text": {"type": "string"},
      "file_path": {"type": "string"}
    }
  }
}
```

4. After registration
   - Use the Foundry Test/Playground to send a sample payload.
   - Tail Function App logs: `az webapp log tail --name <FUNCTION_APP_NAME> --resource-group <RESOURCE_GROUP>`

Security note: For production, use Key Vault or Foundry secrets to store the function key and do not commit secrets to git.
