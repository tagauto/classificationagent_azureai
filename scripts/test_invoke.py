#!/usr/bin/env python3
"""Invoke the deployed Function App /api/invoice with the sample payload.

Behavior:
- If `FUNCTION_URL` and `FUNCTION_KEY` env vars are set, use them.
- Otherwise try to read `azd` environment values (functionAppUrl, functionAppName,
  AZURE_RESOURCE_GROUP) and then call `az functionapp function keys list` to get
  the function key.

Usage:
  python scripts/test_invoke.py

Requires: Python `requests` package and Azure CLI + azd on PATH if env vars not set.
"""
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "samples" / "sample_request.json"


def run(cmd):
    proc = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}\n{proc.stderr}")
    return proc.stdout.strip()


def discover_from_azd():
    # Get azd env values
    out = run("azd env get-values --environment invoice-agent-foundry --output json")
    vals = json.loads(out)
    url = vals.get("functionAppUrl")
    name = vals.get("functionAppName")
    rg = vals.get("AZURE_RESOURCE_GROUP")
    return url, name, rg


def get_function_key(app_name, resource_group, function_name="invoiceprocessor"):
    cmd = f"az functionapp function keys list --name {app_name} --resource-group {resource_group} --function-name {function_name} -o json"
    out = run(cmd)
    keys = json.loads(out)
    # prefer 'default'
    return keys.get("default") or next(iter(keys.values()))


def main():
    function_url = os.getenv("FUNCTION_URL")
    function_key = os.getenv("FUNCTION_KEY")

    if not function_url or not function_key:
        try:
            function_url, function_app_name, resource_group = discover_from_azd()
        except Exception as exc:
            print("Failed to discover function via azd. Set FUNCTION_URL and FUNCTION_KEY env vars.")
            raise

        if not function_url or not function_app_name or not resource_group:
            raise RuntimeError("Missing azd environment values: functionAppUrl/functionAppName/AZURE_RESOURCE_GROUP")

        if not function_key:
            function_key = get_function_key(function_app_name, resource_group)

    if not function_url or not function_key:
        raise RuntimeError("Function URL or key not found")

    api = function_url.rstrip("/") + "/api/invoice"
    payload = json.loads(SAMPLE.read_text())

    headers = {"Content-Type": "application/json", "x-functions-key": function_key}
    resp = requests.post(api, json=payload, headers=headers, timeout=30)
    print(f"POST {api} -> {resp.status_code}")
    print(resp.text)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
