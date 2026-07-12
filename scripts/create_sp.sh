#!/usr/bin/env bash
set -euo pipefail

SUBSCRIPTION_ID="${1:-}"
RESOURCE_GROUP="${2:-}"
SP_NAME="${3:-invoice-agent-foundry}"

if [[ -z "$SUBSCRIPTION_ID" || -z "$RESOURCE_GROUP" ]]; then
  echo "Usage: ./scripts/create_sp.sh <subscription-id> <resource-group> [service-principal-name]" >&2
  exit 1
fi

az account set --subscription "$SUBSCRIPTION_ID"
az ad sp create-for-rbac \
  --name "$SP_NAME" \
  --role contributor \
  --scopes "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP" \
  --output json
