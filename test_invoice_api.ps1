# PowerShell script to test Invoice Processing API

param(
    [string]$FunctionUrl = "https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice",
    [string]$ApiKey = "<AZURE_FUNCTION_KEY>",
    [string]$InvoiceText = "Invoice #INV-2024-001`nVendor: Acme Corporation`nDate: 2024-07-10`nTotal Amount: $1,500.00"
)

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Invoice Processing API Test" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Prepare headers hashtable
$headers = @{
    "x-functions-key" = $ApiKey
    "Content-Type"    = "application/json"
}

# Prepare request body
$body = @{
    text = $InvoiceText
} | ConvertTo-Json

Write-Host "`n[Request Details]" -ForegroundColor Yellow
Write-Host "URL: $FunctionUrl"
Write-Host "Method: POST"
Write-Host "Headers:" -ForegroundColor Gray
$headers.GetEnumerator() | ForEach-Object { Write-Host "  - $($_.Key): $($_.Value.Substring(0, [Math]::Min(20, $_.Value.Length)))..." -ForegroundColor Gray }
Write-Host "Body:" -ForegroundColor Gray
Write-Host $body -ForegroundColor Gray

# Make the request
try {
    Write-Host "`n[Sending Request...]" -ForegroundColor Cyan
    
    $response = Invoke-WebRequest `
        -Uri $FunctionUrl `
        -Method Post `
        -Headers $headers `
        -Body $body `
        -TimeoutSec 30 `
        -ErrorAction Stop
    
    Write-Host "[Success!] Status: $($response.StatusCode)" -ForegroundColor Green
    
    # Parse and display response
    Write-Host "`n[Response]" -ForegroundColor Yellow
    $content = $response.Content | ConvertFrom-Json
    
    Write-Host "`nðŸ“‹ Extracted Fields:" -ForegroundColor Cyan
    $content.extracted_fields | ForEach-Object {
        Write-Host "  Vendor: $($_.vendor_name)"
        Write-Host "  Invoice #: $($_.invoice_number)"
        Write-Host "  Amount: $($_.total_amount)"
        Write-Host "  Date: $($_.invoice_date)"
    }
    
    Write-Host "`nðŸ“Š Analysis:" -ForegroundColor Cyan
    $content.analysis | ForEach-Object {
        Write-Host "  Document Type: $($_.document_type)"
        Write-Host "  Confidence: $($_.confidence)"
        Write-Host "  Issues: $(if ($_.issues.Count -eq 0) { 'None' } else { $_.issues -join ', ' })"
    }
    
    Write-Host "`n[Full Response]" -ForegroundColor Gray
    $content | ConvertTo-Json -Depth 10
    
} catch {
    Write-Host "[Error!]" -ForegroundColor Red
    Write-Host "Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    Write-Host "Message: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $errorContent = $reader.ReadToEnd()
        Write-Host "Response: $errorContent" -ForegroundColor Red
        $reader.Close()
    }
}

