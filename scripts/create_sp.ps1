param(
  [Parameter(Mandatory=$true)] [string]$SubscriptionId,
  [Parameter(Mandatory=$true)] [string]$ResourceGroup,
  [string]$ServicePrincipalName = 'invoice-agent-foundry'
)

az account set --subscription $SubscriptionId
az ad sp create-for-rbac `
  --name $ServicePrincipalName `
  --role contributor `
  --scopes "/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroup" `
  --output json
