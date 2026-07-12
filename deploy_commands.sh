#!/usr/bin/env bash
set -euo pipefail

SUBSCRIPTION_ID="${1:-00000000-0000-0000-0000-000000000000}"
RESOURCE_GROUP="${2:-invoice-agent-rg}"
LOCATION="${3:-eastus}"
AZD_ENV_NAME="${4:-invoice-agent-foundry}"
FUNCTION_APP_NAME="${5:-invoice-agent-foundry-func}"
DOC_INTELLIGENCE_ENDPOINT="${6:-https://<your-resource>.cognitiveservices.azure.com/}"
DOC_INTELLIGENCE_KEY="${7:-<your-key>}"

function ensure_resource_group() {
  local existing_location
  existing_location=$(az group show --name "$RESOURCE_GROUP" --query location -o tsv 2>/dev/null || true)

  if [[ -n "$existing_location" ]]; then
    if [[ "$existing_location" != "$LOCATION" ]]; then
      echo "Resource group '$RESOURCE_GROUP' already exists in location '$existing_location'."
      read -r -p "Use existing location '$existing_location' instead of requested location '$LOCATION'? (Y/n): " choice
      if [[ "$choice" =~ ^[Nn] ]]; then
        read -r -p 'Enter a new resource group name to create: ' new_group
        if [[ -z "$new_group" ]]; then
          echo 'No resource group name provided. Aborting.'
          exit 1
        fi
        RESOURCE_GROUP="$new_group"
        az group create --name "$RESOURCE_GROUP" --location "$LOCATION"
      else
        LOCATION="$existing_location"
      fi
    fi
  else
    az group create --name "$RESOURCE_GROUP" --location "$LOCATION"
  fi
}

function ensure_function_app_name() {
  local existing_location
  existing_location=$(az functionapp show --name "$FUNCTION_APP_NAME" --resource-group "$RESOURCE_GROUP" --query location -o tsv 2>/dev/null || true)

  if [[ -n "$existing_location" ]]; then
    if [[ "$existing_location" != "$LOCATION" ]]; then
      echo "A Function App named '$FUNCTION_APP_NAME' already exists in resource group '$RESOURCE_GROUP' in location '$existing_location'."
      read -r -p 'Enter a different Function App name to create: ' new_name
      if [[ -z "$new_name" ]]; then
        echo 'A different Function App name is required. Aborting.'
        exit 1
      fi
      FUNCTION_APP_NAME="$new_name"
    else
      echo "Using existing Function App '$FUNCTION_APP_NAME' in resource group '$RESOURCE_GROUP'."
    fi
  fi
}

function azd_env_exists() {
  local env_names
  env_names=$(azd env list --query "[].name" -o tsv 2>/dev/null || true)
  printf '%s' "$env_names" | grep -qx "$AZD_ENV_NAME"
}

az login
az account set --subscription "$SUBSCRIPTION_ID"
ensure_resource_group
ensure_function_app_name
azd auth login
if azd_env_exists; then
  echo "Using existing Azure Developer CLI environment '$AZD_ENV_NAME'."
else
  echo "Creating Azure Developer CLI environment '$AZD_ENV_NAME'."
  azd env new "$AZD_ENV_NAME"
fi
azd env set --environment "$AZD_ENV_NAME" AZURE_LOCATION "$LOCATION"
azd env set --environment "$AZD_ENV_NAME" AZURE_RESOURCE_GROUP "$RESOURCE_GROUP"

echo "Updating azd infra config for functionAppName='$FUNCTION_APP_NAME'."
azd env config set --environment "$AZD_ENV_NAME" infra.parameters.functionAppName "$FUNCTION_APP_NAME"

ez_output=$(azd up 2>&1) || {
  if [[ "$ez_output" == *"SubscriptionIsOverQuotaForSku"* ]]; then
    echo "Deployment failed because the subscription quota is insufficient for the requested App Service plan in location '$LOCATION'. Request additional quota for App Service / Total VMs in the Azure portal, or use a different subscription/region." >&2
  elif [[ "$ez_output" == *"InvalidResourceLocation"* ]]; then
    echo "Deployment failed because a resource name already exists in a different Azure location. Use a different Function App name or resource group." >&2
  fi
  echo "$ez_output" >&2
  exit 1
}

echo 'azd up completed successfully.'
if ! az functionapp show --name "$FUNCTION_APP_NAME" --resource-group "$RESOURCE_GROUP" >/dev/null 2>&1; then
  echo "Function App '$FUNCTION_APP_NAME' was not found after azd deployment. Check deployment logs and resource group state." >&2
  exit 1
fi

echo "Verified Function App '$FUNCTION_APP_NAME' exists in resource group '$RESOURCE_GROUP'."
az functionapp config appsettings set \
  --settings \
  AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT="$DOC_INTELLIGENCE_ENDPOINT" \
  AZURE_DOCUMENT_INTELLIGENCE_KEY="$DOC_INTELLIGENCE_KEY" \
  --name "$FUNCTION_APP_NAME" \
  --resource-group "$RESOURCE_GROUP"
