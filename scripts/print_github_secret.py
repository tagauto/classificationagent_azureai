import json
import os
import subprocess
import sys
from typing import Any, Dict


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scripts/print_github_secret.py <subscription-id>")
        sys.exit(1)

    subscription_id = sys.argv[1]
    try:
        result = subprocess.run(
            ["az", "account", "show", "--subscription", subscription_id, "--output", "json"],
            check=True,
            capture_output=True,
            text=True,
        )
        account = json.loads(result.stdout)
        tenant_id = account.get("tenantId")
    except Exception as exc:
        print(f"Unable to read Azure account info: {exc}", file=sys.stderr)
        sys.exit(1)

    payload: Dict[str, Any] = {
        "clientId": "<service-principal-client-id>",
        "clientSecret": "<service-principal-client-secret>",
        "subscriptionId": subscription_id,
        "tenantId": tenant_id,
    }

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
