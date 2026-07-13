# Agent Build & Deployment Plan Using Foundry SDK

## Overview
Build an invoice processing agent using Azure AI Foundry SDK and deploy it programmatically.

---

## Step-by-Step Plan

### Phase 1: Environment & Setup
- [x] Set up Python environment  
- [x] Install `azure-ai-projects` SDK
- [ ] Create Foundry client connection
- [ ] Load OpenAPI schema for invoice tool

### Phase 2: Agent Definition
- [ ] Create agent manifest (YAML or JSON format)
- [ ] Define system instructions for the agent
- [ ] Define available tools (invoice API)
- [ ] Set model configuration (gpt-4o-mini)

### Phase 3: Agent Creation
- [ ] Use SDK to create agent version from manifest
- [ ] Register OpenAPI tool with the agent
- [ ] Configure authentication headers
- [ ] Test agent locally with sample inputs

### Phase 4: Deployment
- [ ] Deploy agent to Azure AI Foundry
- [ ] Activate agent version
- [ ] Verify agent appears in Foundry UI
- [ ] Get agent ID and access URL

### Phase 5: Testing & Validation
- [ ] Test agent through Foundry UI
- [ ] Verify OpenAPI tool integration works
- [ ] Verify invoice processing end-to-end
- [ ] Check error handling and edge cases

### Phase 6: Cleanup
- [ ] Remove test scripts and temporary files
- [ ] Archive deployment logs
- [ ] Document final configuration
- [ ] Create deployment summary

---

## Key Implementation Details

### Agent Manifest Structure
```yaml
kind: agent
name: invoice-agent
description: Invoice extraction and analysis using Document Intelligence
model: gpt-4o-mini
instructions: "You are an invoice processing assistant..."
tools:
  - type: openapi
    name: invoice_processor
    spec: <openapi_schema>
    auth:
      type: header
      name: x-functions-key
      value: <FUNCTION_KEY>
```

### SDK Methods Used
- `AIProjectClient()` - Connect to Foundry
- `client.agents.create_version_from_manifest()` - Create agent from manifest
- `client.agents.get()` - Retrieve agent details
- `client.agents.list()` - List all agents
- `client.agents.enable()` - Activate agent

### Authentication Flow
1. `DefaultAzureCredential()` for Foundry authentication
2. Function key in OpenAPI auth header
3. Token audience: `https://ai.azure.com`

---

## Expected Outcomes

✅ Agent deployed to: `https://ai.azure.com/projects/tagoreautomation-2862/agents/<agent-id>`
✅ Agent can process invoice requests
✅ Returns extracted fields + analysis
✅ Integrated with Azure Document Intelligence
✅ Full programmatic deployment (no manual UI steps)

---

## Files Generated
- `agent_manifest.yaml` - Agent definition
- `build_agent_sdk.py` - Build script
- `test_agent_local.py` - Local testing script
- `deploy_agent_sdk.py` - Final deployment script
- `DEPLOYMENT_SUMMARY.md` - Deployment record
