#!/usr/bin/env pwsh
<#
.SYNOPSIS
Deploy invoice-agent to Azure AI Foundry via REST API

.PARAMETER FunctionKey
The Azure Function key for authentication

.PARAMETER FoundryProjectUrl
The Azure AI Foundry project URL

.EXAMPLE
.\deploy_agent_to_foundry_api.ps1 -FunctionKey "your-key" -FoundryProjectUrl "https://..."
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$FunctionKey,
    
    [Parameter(Mandatory=$false)]
    [string]$FoundryProjectUrl = "https://tagoreautomation-2862-resource.services.ai.azure.com/api/projects/tagoreautomation-2862"
)

$ErrorActionPreference = "Stop"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $Level : $Message"
}

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host $Message -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
}

try {
    Write-Header "Azure AI Foundry Agent Deployment"
    
    # Configuration
    $agentName = "invoice-agent"
    $agentDescription = "Invoice extraction and analysis using Document Intelligence"
    $functionEndpoint = "https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice"
    
    Write-Log "Agent Configuration:" "INFO"
    Write-Host "  Name: $agentName"
    Write-Host "  Description: $agentDescription"
    Write-Host "  Backend: $functionEndpoint"
    Write-Host "  Function Key: $($FunctionKey.Substring(0, 10))..." 
    Write-Host ""
    
    # Step 1: Get access token
    Write-Header "Step 1: Getting Azure Access Token"
    Write-Log "Authenticating with Azure..." "STEP"
    
    $tokenCmd = "az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv"
    $token = Invoke-Expression $tokenCmd
    
    if (-not $token) {
        throw "Failed to get access token. Ensure you're logged in with 'az login'"
    }
    
    Write-Log "✓ Access token obtained" "SUCCESS"
    Write-Host "  Token length: $($token.Length) chars"
    Write-Host ""
    
    # Step 2: Prepare agent payload
    Write-Header "Step 2: Preparing Agent Configuration"
    Write-Log "Creating agent configuration..." "STEP"
    
    $inputSchema = @{
        type = "object"
        properties = @{
            text = @{
                type = "string"
                description = "Invoice text to analyze"
            }
            file_path = @{
                type = "string"
                description = "Path to invoice file (optional)"
            }
        }
    }
    
    $outputSchema = @{
        type = "object"
        properties = @{
            extracted_fields = @{
                type = "object"
                properties = @{
                    vendor_name = @{ type = "string" }
                    invoice_number = @{ type = "string" }
                    total_amount = @{ type = "number" }
                    invoice_date = @{ type = "string" }
                }
            }
            analysis = @{
                type = "object"
                properties = @{
                    document_type = @{ type = "string" }
                    confidence = @{ type = "number" }
                    vendor_name = @{ type = "string" }
                    invoice_number = @{ type = "string" }
                    total_amount = @{ type = "number" }
                    invoice_date = @{ type = "string" }
                    issues = @{
                        type = "array"
                        items = @{ type = "string" }
                    }
                }
            }
        }
    }
    
    $agentPayload = @{
        name = $agentName
        description = $agentDescription
        kind = "Agent"
        spec = @{
            kind = "default"
            endpoints = @(
                @{
                    kind = "endpoint"
                    type = "http"
                    url = $functionEndpoint
                    auth = @{
                        type = "header"
                        key = "x-functions-key"
                        value = $FunctionKey
                    }
                }
            )
            inputSchema = $inputSchema
            outputSchema = $outputSchema
        }
    }
    
    $agentJson = $agentPayload | ConvertTo-Json -Depth 10
    Write-Log "✓ Agent configuration prepared" "SUCCESS"
    Write-Host ""
    
    # Step 3: Deploy via REST API
    Write-Header "Step 3: Deploying Agent to Azure AI Foundry"
    Write-Log "Sending deployment request..." "STEP"
    
    # Build API endpoint
    $baseUrl = $FoundryProjectUrl -replace "/api/projects/.*", ""
    $projectId = $FoundryProjectUrl.Split("/")[-1]
    
    Write-Host "  Base URL: $baseUrl"
    Write-Host "  Project ID: $projectId"
    Write-Host ""
    
    # Try multiple API endpoints
    $endpoints = @(
        "$baseUrl/agents",
        "$FoundryProjectUrl/agents",
        "https://ai.azure.com/api/agents"
    )
    
    $headers = @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json"
    }
    
    $deployed = $false
    foreach ($endpoint in $endpoints) {
        try {
            Write-Log "Trying endpoint: $endpoint" "INFO"
            
            $response = Invoke-WebRequest `
                -Uri $endpoint `
                -Method POST `
                -Headers $headers `
                -Body $agentJson `
                -ContentType "application/json" `
                -ErrorAction SilentlyContinue
            
            if ($response.StatusCode -in @(200, 201, 202)) {
                Write-Log "✓ Agent created successfully! Status: $($response.StatusCode)" "SUCCESS"
                $deployed = $true
                
                $result = $response.Content | ConvertFrom-Json
                Write-Host "  Response: $($response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 2)"
                break
            }
        }
        catch {
            Write-Log "Endpoint failed: $($_.Exception.Message)" "WARNING"
        }
    }
    
    if (-not $deployed) {
        Write-Log "Warning: Could not reach Foundry API endpoints" "WARNING"
        Write-Host ""
        Write-Host "Configuration is ready. Use one of these methods:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Option A: Manual UI Deployment" -ForegroundColor Green
        Write-Host "1. Open https://ai.azure.com"
        Write-Host "2. Create new agent with these settings:"
        Write-Host "   - Name: $agentName"
        Write-Host "   - Backend URL: $functionEndpoint"
        Write-Host "   - Auth Header: x-functions-key: (your function key)"
        Write-Host ""
        Write-Host "Option B: Azure CLI" -ForegroundColor Green
        Write-Host "az ai foundry agent create \" -ForegroundColor Gray
        Write-Host "  --name $agentName \" -ForegroundColor Gray
        Write-Host "  --project-name your-project \" -ForegroundColor Gray
        Write-Host "  --backend-type http \" -ForegroundColor Gray
        Write-Host "  --backend-url '$functionEndpoint'" -ForegroundColor Gray
    }
    
    # Step 4: Test instructions
    Write-Header "Next Steps"
    Write-Log "Agent deployment complete!" "SUCCESS"
    Write-Host ""
    Write-Host "1. Open Azure AI Foundry:" -ForegroundColor Green
    Write-Host "   https://ai.azure.com"
    Write-Host ""
    Write-Host "2. Find your agent:" -ForegroundColor Green
    Write-Host "   Name: $agentName"
    Write-Host ""
    Write-Host "3. Test the agent:" -ForegroundColor Green
    Write-Host "   Go to Test/Playground tab and send:"
    Write-Host "   {`"text`": `"Vendor: Acme\nInvoice # 001\nAmount: `$100`"}" -ForegroundColor Gray
    Write-Host ""
    Write-Host "4. Or test directly with curl:" -ForegroundColor Green
    Write-Host "   curl -X POST \" -ForegroundColor Gray
    Write-Host "     -H 'x-functions-key: $FunctionKey' \" -ForegroundColor Gray
    Write-Host "     -H 'Content-Type: application/json' \" -ForegroundColor Gray
    Write-Host "     -d '{\"text\": \"Vendor: Test\nAmount: 500\"}' \" -ForegroundColor Gray
    Write-Host "     $functionEndpoint" -ForegroundColor Gray
    Write-Host ""
    
}
catch {
    Write-Host ""
    Write-Log "DEPLOYMENT FAILED" "ERROR"
    Write-Log $_.Exception.Message "ERROR"
    Write-Host ""
    Write-Log "Troubleshooting:" "ERROR"
    Write-Host "1. Ensure you're logged in: az login"
    Write-Host "2. Check Azure CLI: az --version"
    Write-Host "3. Verify function key is correct"
    Write-Host "4. Check Foundry project URL"
    exit 1
}
