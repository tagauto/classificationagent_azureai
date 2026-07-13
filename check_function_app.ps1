# Check if the Azure Function App is up and responding

$FunctionUrl = "https://invoice-agent-docintelligence2.azurewebsites.net"
$ApiKey = "<AZURE_FUNCTION_KEY>"

Write-Host "Testing Function App connectivity..." -ForegroundColor Cyan

# Test 1: Simple health check
Write-Host "`n[1] Testing base URL..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-WebRequest -Uri $FunctionUrl -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
    Write-Host "âœ“ Base URL responds: $($healthResponse.StatusCode)" -ForegroundColor Green
}
catch {
    Write-Host "âœ— Base URL failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Check /api endpoint
Write-Host "`n[2] Testing /api endpoint..." -ForegroundColor Yellow
try {
    $apiResponse = Invoke-WebRequest -Uri "$FunctionUrl/api" -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
    Write-Host "âœ“ /api endpoint responds: $($apiResponse.StatusCode)" -ForegroundColor Green
}
catch {
    Write-Host "âœ— /api endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Check /api/invoice endpoint
Write-Host "`n[3] Testing /api/invoice endpoint..." -ForegroundColor Yellow
try {
    # Try GET first to see if endpoint exists
    $invoiceResponse = Invoke-WebRequest -Uri "$FunctionUrl/api/invoice" -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
    Write-Host "âœ“ /api/invoice responds: $($invoiceResponse.StatusCode)" -ForegroundColor Green
}
catch {
    Write-Host "Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    Write-Host "Message: $($_.Exception.Message)" -ForegroundColor Red
    
    # Try to get error details
    if ($_.Exception.Response) {
        try {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $errorContent = $reader.ReadToEnd()
            Write-Host "Response Body: $errorContent" -ForegroundColor Gray
            $reader.Close()
        }
        catch {}
    }
}

# Test 4: Try POST with proper headers
Write-Host "`n[4] Testing POST with invoice data..." -ForegroundColor Yellow
try {
    $headers = @{
        "x-functions-key" = $ApiKey
        "Content-Type"    = "application/json"
    }
    
    $body = @{
        text = "Test Invoice"
    } | ConvertTo-Json
    
    $postResponse = Invoke-WebRequest `
        -Uri "$FunctionUrl/api/invoice" `
        -Method Post `
        -Headers $headers `
        -Body $body `
        -TimeoutSec 10 `
        -UseBasicParsing
        
    Write-Host "âœ“ POST succeeded: $($postResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($postResponse.Content)" -ForegroundColor Green
}
catch {
    Write-Host "POST failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        try {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $errorContent = $reader.ReadToEnd()
            Write-Host "Error Details: $errorContent" -ForegroundColor Yellow
            $reader.Close()
        }
        catch {}
    }
}

