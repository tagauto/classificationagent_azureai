# PowerShell script to test Invoice Processing API

param(
    [string]$FunctionUrl = "https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice",
    [string]$ApiKey = "<AZURE_FUNCTION_KEY>",
    [string]$InvoiceText = "Invoice #INV-2024-001`nVendor: Acme Corporation`nDate: 2024-07-10`nTotal: $1,500.00"
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

# Make the request
try {
    Write-Host "`n[Sending Request...]" -ForegroundColor Cyan
    
    $response = Invoke-WebRequest `
        -Uri $FunctionUrl `
        -Method Post `
        -Headers $headers `
        -Body $body `
        -TimeoutSec 30
    
    Write-Host "[Success!] Status: $($response.StatusCode)" -ForegroundColor Green
    
    # Parse and display response
    Write-Host "`n[Response]" -ForegroundColor Yellow
    $content = $response.Content | ConvertFrom-Json
    
    Write-Host "`nExtracted Fields:" -ForegroundColor Cyan
    Write-Host "  Vendor: $($content.extracted_fields.vendor_name)"
    Write-Host "  Invoice #: $($content.extracted_fields.invoice_number)"
    Write-Host "  Amount: $($content.extracted_fields.total_amount)"
    Write-Host "  Date: $($content.extracted_fields.invoice_date)"
    
    Write-Host "`nAnalysis:" -ForegroundColor Cyan
    Write-Host "  Document Type: $($content.analysis.document_type)"
    Write-Host "  Confidence: $($content.analysis.confidence)"
    Write-Host "  Issues: $(if ($content.analysis.issues.Count -eq 0) { 'None' } else { $content.analysis.issues -join ', ' })"
    
    Write-Host "`n[Full Response JSON]" -ForegroundColor Gray
    $content | ConvertTo-Json -Depth 10
    
}
catch {
    Write-Host "[Error!]" -ForegroundColor Red
    Write-Host "Message: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        Write-Host "Status Code: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    }
}

