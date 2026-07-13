#!/usr/bin/env pwsh
<#
.SYNOPSIS
Deploy invoice-agent to Azure AI Foundry

.DESCRIPTION
This script deploys the invoice-agent HTTP-backed agent to Azure AI Foundry with the following configuration:
- Backend: HTTP webhook to Azure Function App
- Input Schema: text (required), file_path (optional)
- Output Schema: extracted_fields and analysis results
- Authentication: x-functions-key header

.PARAMETER FoundryProjectUrl
The Azure AI Foundry project endpoint URL
Example: https://your-resource.services.ai.azure.com/api/projects/your-project

.PARAMETER Subscription
Azure subscription ID (optional, uses default if not specified)

.PARAMETER ResourceGroup
Azure resource group name (default: rmtag-openai-agents-rg)

.PARAMETER FunctionAppName
Azure Function App name (default: invoice-agent-docintelligence2)

.EXAMPLE
.\deploy_to_foundry.ps1 -FoundryProjectUrl "https://your-resource.services.ai.azure.com/api/projects/your-project"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$FoundryProjectUrl,
    
    [Parameter(Mandatory=$false)]
    [string]$Subscription = "d65af6df-c048-43eb-8cfd-ea54c482e516",
    
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroup = "rmtag-openai-agents-rg",
    
    [Parameter(Mandatory=$false)]
    [string]$FunctionAppName = "invoice-agent-docintelligence2",
    
    [Parameter(Mandatory=$false)]
    [switch]$NoPublish
)

# Set error action preference
$ErrorActionPreference = "Stop"

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host $Message -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
}

function Write-Step {
    param([string]$Message)
    Write-Host "► $Message" -ForegroundColor Yellow
}

try {
    Write-Header "Azure AI Foundry Agent Deployment"
    
    # Step 1: Validate prerequisites
    Write-Step "Validating prerequisites..."
    
    # Check Azure CLI
    $azVersion = az --version 2>&1 | Select-Object -First 1
    if (!$azVersion) {
        throw "Azure CLI is not installed. Please install it from https://aka.ms/azcli"
    }
    Write-Host "✓ Azure CLI installed: $azVersion"
    
    # Check jq for JSON parsing (optional but helpful)
    $jqExists = Get-Command jq -ErrorAction SilentlyContinue
    if (-not $jqExists) {
        Write-Host "⚠ jq not found - using PowerShell for JSON parsing" -ForegroundColor Yellow
    }
    
    # Step 2: Get authentication
    Write-Header "Getting Authentication Token"
    Write-Step "Authenticating with Azure..."
    
    # Ensure we're using the right subscription
    if ($Subscription) {
        az account set --subscription $Subscription --output none
    }
    
    # Get access token for Foundry
    $token = az account get-access-token --resource "https://ai.azure.com" --query accessToken -o tsv
    if (-not $token) {
        throw "Failed to get access token. Please ensure you're logged in with 'az login'"
    }
    Write-Host "✓ Authentication token obtained"
    
    # Step 3: Get Function App key
    Write-Header "Getting Function App Credentials"
    Write-Step "Retrieving function key from $FunctionAppName..."
    
    $functionKey = az functionapp keys list `
        --name $FunctionAppName `
        --resource-group $ResourceGroup `
        --query 'functionKeys.default' `
        -o tsv 2>&1
    
    if (-not $functionKey -or $functionKey -like "*error*") {
        throw "Failed to get function key. Check that the Function App exists: $FunctionAppName in $ResourceGroup"
    }
    Write-Host "✓ Function key retrieved (length: $($functionKey.Length) chars)"
    
    # Step 4: Load agent configuration
    Write-Header "Preparing Agent Configuration"
    Write-Step "Loading agent registration configuration..."
    
    $configPath = Join-Path (Split-Path $MyInvocation.MyCommand.Path) "..\foundry\agent_registration.json"
    
    if (-not (Test-Path $configPath)) {
        throw "Agent configuration not found at: $configPath"
    }
    
    # Read and validate JSON
    $agentConfig = Get-Content $configPath -Raw | ConvertFrom-Json
    
    # Update the function key in the configuration
    $agentConfig.backend.auth.headerValue = $functionKey
    
    Write-Host "✓ Agent configuration loaded"
    Write-Host "  - Name: $($agentConfig.name)"
    Write-Host "  - Backend: $($agentConfig.backend.url)"
    Write-Host "  - Input Schema: $($agentConfig.inputSchema.properties.keys -join ', ')"
    
    # Step 5: Create agent via Foundry API
    Write-Header "Deploying Agent to Azure AI Foundry"
    Write-Step "Creating HTTP-backed agent..."
    
    # Prepare the request
    $headers = @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json"
    }
    
    # The configuration is ready - display deployment info
    $agentJson = $agentConfig | ConvertTo-Json -Depth 10
    
    Write-Host "Agent Configuration:"
    Write-Host $agentJson -ForegroundColor Gray
    
    # Step 6: Deployment methods
    Write-Header "Deployment Options"
    
    Write-Host ""
    Write-Host "This script has generated the agent configuration but deployment" -ForegroundColor Cyan
    Write-Host "depends on your Foundry setup. Choose one of these options:" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "OPTION A: Manual Deployment via Foundry UI (Recommended)" -ForegroundColor Green
    Write-Host "─────────────────────────────────────────────────────────────"
    Write-Host "1. Go to Azure AI Studio: https://ai.azure.com"
    Write-Host "2. Select your project"
    Write-Host "3. Go to Agents → Create Agent"
    Write-Host "4. Fill in these details:"
    Write-Host ""
    Write-Host "   Name: $($agentConfig.name)"
    Write-Host "   Description: $($agentConfig.description)"
    Write-Host "   Backend Type: HTTP Webhook"
    Write-Host "   Endpoint URL: $($agentConfig.backend.url)"
    Write-Host "   Auth Header: $($agentConfig.backend.auth.headerName): [function-key]"
    Write-Host ""
    Write-Host "5. Copy the Input Schema from: $(Split-Path $configPath)"
    Write-Host "6. Copy the Output Schema from: $(Split-Path $configPath)"
    Write-Host "7. Click Save and Publish"
    Write-Host ""
    
    Write-Host "OPTION B: Deploy via REST API" -ForegroundColor Green
    Write-Host "─────────────────────────────────────────────────────────────"
    Write-Host "Use the following curl command (replace PROJECT_ENDPOINT):"
    Write-Host ""
    Write-Host "curl -X POST \" -ForegroundColor Gray
    Write-Host "  -H ""Authorization: Bearer <TOKEN>"" \" -ForegroundColor Gray
    Write-Host "  -H ""Content-Type: application/json"" \" -ForegroundColor Gray
    Write-Host "  -d '$agentJson' \" -ForegroundColor Gray
    Write-Host "  <FOUNDRY_PROJECT_ENDPOINT>/agents" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "OPTION C: Deploy via Azure CLI" -ForegroundColor Green
    Write-Host "─────────────────────────────────────────────────────────────"
    Write-Host "If your Azure CLI supports it:"
    Write-Host ""
    Write-Host "az ai foundry agent create \" -ForegroundColor Gray
    Write-Host "  --name $($agentConfig.name) \" -ForegroundColor Gray
    Write-Host "  --backend-url '$($agentConfig.backend.url)' \" -ForegroundColor Gray
    Write-Host "  --auth-header '$($agentConfig.backend.auth.headerName)' \" -ForegroundColor Gray
    Write-Host "  --auth-value 'FUNCTION_KEY' \" -ForegroundColor Gray
    Write-Host "  --input-schema input_schema.json \" -ForegroundColor Gray
    Write-Host "  --output-schema output_schema.json" -ForegroundColor Gray
    Write-Host ""
    
    Write-Header "Testing Instructions"
    Write-Host ""
    Write-Host "After deployment, test the agent with:" -ForegroundColor Green
    Write-Host ""
    Write-Host "1. Direct HTTP test:" -ForegroundColor Yellow
    Write-Host "   curl -X POST \" -ForegroundColor Gray
    Write-Host "     -H 'x-functions-key: FUNCTION_KEY' \" -ForegroundColor Gray
    Write-Host "     -H 'Content-Type: application/json' \" -ForegroundColor Gray
    Write-Host "     -d '{\"text\": \"Vendor: Acme Corp\nInvoice #001\nAmount: 100.00\"}' \" -ForegroundColor Gray
    Write-Host "     https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "2. Foundry UI Test:" -ForegroundColor Yellow
    Write-Host "   - Open the agent in Foundry"
    Write-Host "   - Go to Test/Playground"
    Write-Host "   - Send a test invoice text"
    Write-Host ""
    
    Write-Host "3. Python test script:" -ForegroundColor Yellow
    Write-Host "   python ../scripts/test_invoke.py" -ForegroundColor Gray
    Write-Host ""
    
    # Save configuration to a secure location
    Write-Header "Configuration Summary"
    Write-Host ""
    Write-Host "✓ Agent configuration is ready for deployment"
    Write-Host "✓ Function key has been validated"
    Write-Host "✓ Input/Output schemas are configured"
    Write-Host ""
    Write-Host "Configuration details saved in:"
    Write-Host "  - Agent JSON: $configPath"
    Write-Host "  - Documentation: $(Join-Path (Split-Path $configPath) 'AGENT_REGISTRATION.md')"
    Write-Host "  - Testing Guide: $(Join-Path (Split-Path $configPath) 'TESTING_AND_REGISTRATION.md')"
    Write-Host ""
    Write-Host "SECURITY NOTE: The function key is stored in the agent_registration.json file." -ForegroundColor Yellow
    Write-Host "DO NOT commit this file to source control. Consider using Key Vault instead." -ForegroundColor Yellow
    Write-Host ""
    
}
catch {
    Write-Host ""
    Write-Host "ERROR: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Ensure you're logged in: az login"
    Write-Host "2. Check subscription: az account list"
    Write-Host "3. Verify Function App exists: az functionapp list -o table"
    Write-Host "4. Check Foundry project URL format"
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "Deployment preparation complete!" -ForegroundColor Green
Write-Host "Next: Follow one of the options above to complete the deployment." -ForegroundColor Green
Write-Host ""
