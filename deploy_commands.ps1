param(
  [string]$SubscriptionId = '00000000-0000-0000-0000-000000000000',
  [string]$ResourceGroup = 'invoice-agent-rg',
  [string]$Location = 'eastus',
  [string]$AzdEnvName = 'invoice-agent-foundry',
  [string]$FunctionAppName = 'invoice-agent-foundry-func',
  [string]$DocIntelligenceEndpoint = 'https://<your-resource>.cognitiveservices.azure.com/',
  [string]$DocIntelligenceKey = '<your-key>'
)

function Get-AzdEnvironmentNames {
    $azdEnvList = azd env list --query "[].name" -o tsv 2>$null
    if ($LASTEXITCODE -eq 0 -and $azdEnvList) {
        return $azdEnvList -split "`n"
    }
    return @()
}

function Ensure-ResourceGroup {
    $existing = az group show --name $ResourceGroup -o json 2>$null | ConvertFrom-Json
    if ($LASTEXITCODE -eq 0) {
        if ($existing.location -ne $Location) {
            Write-Host "Resource group '$ResourceGroup' already exists in location '$($existing.location)'."
            $useExistingLocation = Read-Host "Use existing location '$($existing.location)' instead of requested location '$Location'? (Y/n)"
            if ($useExistingLocation -match '^(n|N)') {
                $newGroup = Read-Host 'Enter a new resource group name to create'
                if (-not $newGroup) {
                    throw 'Resource group name is required when not using the existing location.'
                }
                $ResourceGroup = $newGroup
                az group create --name $ResourceGroup --location $Location | Out-Null
            } else {
                $Location = $existing.location
            }
        }
        return
    }

    az group create --name $ResourceGroup --location $Location | Out-Null
}

function Ensure-FunctionAppName {
    $existingApp = az functionapp show --name $FunctionAppName --resource-group $ResourceGroup 2>$null | ConvertFrom-Json
    if ($LASTEXITCODE -eq 0) {
        if ($existingApp.location -ne $Location) {
            Write-Host "A Function App named '$FunctionAppName' already exists in resource group '$ResourceGroup' with location '$($existingApp.location)'."
            $newName = Read-Host 'Enter a different Function App name to create'
            if (-not $newName) {
                throw 'A different Function App name is required when the existing app is in a different location.'
            }
            $FunctionAppName = $newName
        } else {
            Write-Host "Using existing Function App '$FunctionAppName' in resource group '$ResourceGroup'."
        }
    }
}

function Ensure-AzdEnvironment {
    $envNames = Get-AzdEnvironmentNames
    if ($envNames -contains $AzdEnvName) {
        Write-Host "Using existing Azure Developer CLI environment '$AzdEnvName'."
        return
    }

    Write-Host "Creating Azure Developer CLI environment '$AzdEnvName'."
    azd env new $AzdEnvName
}

function Ensure-AzdInfraConfig {
    Write-Host "Updating azd infra config for functionAppName='$FunctionAppName'."
    azd env config set --environment $AzdEnvName infra.parameters.functionAppName $FunctionAppName
}

az login
az account set --subscription $SubscriptionId
Ensure-ResourceGroup
Ensure-FunctionAppName
azd auth login
Ensure-AzdEnvironment
azd env set --environment $AzdEnvName AZURE_LOCATION $Location
azd env set --environment $AzdEnvName AZURE_RESOURCE_GROUP $ResourceGroup
Ensure-AzdInfraConfig
$azdOutput = azd up 2>&1
if ($LASTEXITCODE -ne 0) {
    if ($azdOutput -match 'SubscriptionIsOverQuotaForSku') {
        throw "Deployment failed because the subscription quota is insufficient for the requested App Service plan in location '$Location'. Request additional quota for App Service / Total VMs in Azure portal or use a different subscription or region.\nDetails: $azdOutput"
    }
    if ($azdOutput -match 'InvalidResourceLocation') {
        throw "Deployment failed because a resource name already exists in a different location. Use a different Function App name or resource group.\nDetails: $azdOutput"
    }
    throw "azd up failed. Deployment did not complete.\nDetails: $azdOutput"
}
Write-Host 'azd up completed successfully.'

$functionApp = az functionapp show --name $FunctionAppName --resource-group $ResourceGroup 2>$null | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) {
    throw "Function App '$FunctionAppName' was not found after azd deployment. Check deployment logs and resource group state."
}
Write-Host "Verified Function App '$FunctionAppName' exists in resource group '$ResourceGroup'."

az functionapp config appsettings set `
  --settings `
  AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=$DocIntelligenceEndpoint `
  AZURE_DOCUMENT_INTELLIGENCE_KEY=$DocIntelligenceKey `
  --name $FunctionAppName `
  --resource-group $ResourceGroup
