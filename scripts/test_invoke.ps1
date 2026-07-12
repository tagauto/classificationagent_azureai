# PowerShell test invoker for the Function App /api/invoice
# Usage: powershell -ExecutionPolicy Bypass -File scripts/test_invoke.ps1

$functionUrl = $env:FUNCTION_URL
$functionKey = $env:FUNCTION_KEY

if (-not $functionUrl -or -not $functionKey) {
    Write-Host "Discovering function URL and name via azd..."
    $azdOut = azd env get-values --environment invoice-agent-foundry --output json
    $vals = $azdOut | ConvertFrom-Json
    if (-not $functionUrl) { $functionUrl = $vals.functionAppUrl }
    $functionAppName = $vals.functionAppName
    $resourceGroup = $vals.AZURE_RESOURCE_GROUP

    if (-not $functionKey) {
        Write-Host "Retrieving function key via az CLI..."
        $keysJson = az functionapp function keys list --name $functionAppName --resource-group $resourceGroup --function-name invoiceprocessor -o json
        $keys = $keysJson | ConvertFrom-Json
        $functionKey = $keys.default
    }
}

if (-not $functionUrl -or -not $functionKey) {
    Write-Error "Function URL or key not found. Set FUNCTION_URL and FUNCTION_KEY environment variables or ensure az/azd are installed and logged in."
    exit 1
}

$api = $functionUrl.TrimEnd('/') + "/api/invoice"
Write-Host "Posting to $api"

# Use curl.exe to avoid PowerShell Invoke-WebRequest header conversion issues
# Build curl command using string concatenation to safely include the key and URL
$curl = 'curl.exe -s -X POST -H "Content-Type: application/json" -H "x-functions-key: ' + $functionKey + '" -d @samples/sample_request.json ' + $api
Invoke-Expression $curl
Write-Host "`nDone." 
