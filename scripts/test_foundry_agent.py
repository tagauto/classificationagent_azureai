#!/usr/bin/env python3
"""
Test script for invoice-agent HTTP endpoint

This script tests the invoice-agent deployed to Azure Function App.
It can test both the raw HTTP endpoint and the Foundry agent integration.

Usage:
    python test_foundry_agent.py --help
    python test_foundry_agent.py --direct  # Test Function App directly
    python test_foundry_agent.py --foundry <agent-id>  # Test via Foundry

Requirements:
    - requests library: pip install requests
    - Azure CLI for authentication: az login
"""

import argparse
import json
import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import requests
except ImportError:
    print("ERROR: requests library not found. Install with: pip install requests")
    sys.exit(1)


class InvoiceAgentTester:
    """Test utility for invoice-agent"""
    
    def __init__(self, 
                 function_url: str = "https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice",
                 resource_group: str = "rmtag-openai-agents-rg",
                 function_app: str = "invoice-agent-docintelligence2"):
        """Initialize the tester"""
        self.function_url = function_url
        self.resource_group = resource_group
        self.function_app = function_app
        self.function_key = None
        self.headers = {
            "Content-Type": "application/json"
        }
    
    def get_function_key(self) -> str:
        """Get function key from Azure"""
        print("📋 Retrieving function key from Azure...")
        try:
            result = subprocess.run([
                "az", "functionapp", "keys", "list",
                "--name", self.function_app,
                "--resource-group", self.resource_group,
                "--query", "functionKeys.default",
                "-o", "tsv"
            ], capture_output=True, text=True, check=True)
            
            key = result.stdout.strip()
            if not key:
                raise Exception("Function key is empty")
            
            self.function_key = key
            print(f"✓ Function key retrieved (length: {len(key)})")
            return key
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to get function key: {e.stderr}")
            print("\nTroubleshooting:")
            print(f"  - Verify Azure CLI is installed: az --version")
            print(f"  - Verify you're logged in: az login")
            print(f"  - Check function app exists: az functionapp show --name {self.function_app} --resource-group {self.resource_group}")
            sys.exit(1)
    
    def test_direct_http(self, payload: Dict[str, Any]) -> bool:
        """Test the Function App directly via HTTP"""
        print("\n" + "="*60)
        print("🧪 Test 1: Direct HTTP Request to Function App")
        print("="*60)
        
        if not self.function_key:
            self.get_function_key()
        
        headers = self.headers.copy()
        headers["x-functions-key"] = self.function_key
        
        print(f"\n📤 Sending request to: {self.function_url}")
        print(f"📋 Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(
                self.function_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            print(f"\n📨 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✓ SUCCESS - Agent responded successfully")
                print(f"\n📊 Response:\n{json.dumps(result, indent=2)}")
                
                # Validate response structure
                if "extracted_fields" in result and "analysis" in result:
                    print("\n✓ Response structure is valid")
                    
                    # Check if required fields are extracted
                    extracted = result.get("extracted_fields", {})
                    print(f"\n✓ Extracted Fields:")
                    print(f"  - Vendor: {extracted.get('vendor_name', 'N/A')}")
                    print(f"  - Invoice #: {extracted.get('invoice_number', 'N/A')}")
                    print(f"  - Amount: ${extracted.get('total_amount', 'N/A')}")
                    print(f"  - Date: {extracted.get('invoice_date', 'N/A')}")
                    
                    analysis = result.get("analysis", {})
                    print(f"\n✓ Analysis Results:")
                    print(f"  - Document Type: {analysis.get('document_type', 'N/A')}")
                    print(f"  - Confidence: {analysis.get('confidence', 'N/A')}")
                    
                    if analysis.get("issues"):
                        print(f"  - Issues: {', '.join(analysis['issues'])}")
                    else:
                        print(f"  - Issues: None ✓")
                else:
                    print("⚠ Response structure doesn't match expected schema")
                
                return True
            else:
                print(f"✗ FAILED - HTTP {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            print("✗ TIMEOUT - Request took too long (30s)")
            return False
        except requests.exceptions.ConnectionError as e:
            print(f"✗ CONNECTION ERROR - {e}")
            print("\nTroubleshooting:")
            print(f"  - Verify Function App is running")
            print(f"  - Check URL: {self.function_url}")
            return False
        except Exception as e:
            print(f"✗ ERROR - {e}")
            return False
    
    def test_health_check(self) -> bool:
        """Test Function App health"""
        print("\n" + "="*60)
        print("🏥 Test 0: Function App Health Check")
        print("="*60)
        
        print(f"\n📍 Checking Function App: {self.function_app}")
        
        try:
            result = subprocess.run([
                "az", "functionapp", "show",
                "--name", self.function_app,
                "--resource-group", self.resource_group,
                "--query", "state",
                "-o", "tsv"
            ], capture_output=True, text=True, check=True)
            
            state = result.stdout.strip()
            if state == "Running":
                print(f"✓ Function App is {state}")
                return True
            else:
                print(f"✗ Function App state: {state}")
                return False
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to check status: {e.stderr}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*70)
        print("🚀 Invoice Agent Test Suite")
        print("="*70)
        
        # Test data
        test_payloads = [
            {
                "name": "Valid Invoice",
                "text": "Vendor: Acme Corporation\nInvoice #INV-2026-001\nDate: 2026-07-12\nTotal Amount: $1,250.00"
            },
            {
                "name": "Minimal Invoice",
                "text": "Invoice 123"
            },
            {
                "name": "Complex Invoice",
                "text": """
                From: Northwind Suppliers
                Invoice #NW-2026-1234
                Invoice Date: July 12, 2026
                Due Date: July 26, 2026
                
                Items:
                - Item 1: $500.00
                - Item 2: $750.00
                
                Total Amount Due: $1,250.00
                """
            }
        ]
        
        results = []
        
        # Health check
        health_ok = self.test_health_check()
        
        # Run tests
        for i, payload in enumerate(test_payloads, 1):
            test_name = payload.pop("name")
            print(f"\n\n{'='*70}")
            print(f"Test {i}: {test_name}")
            print(f"{'='*70}")
            
            success = self.test_direct_http(payload)
            results.append((test_name, success))
            
            if i < len(test_payloads):
                print("\n⏳ Waiting before next test...")
                import time
                time.sleep(2)
        
        # Summary
        print("\n" + "="*70)
        print("📊 Test Summary")
        print("="*70)
        
        for test_name, success in results:
            status = "✓ PASS" if success else "✗ FAIL"
            print(f"{status}: {test_name}")
        
        total = len(results)
        passed = sum(1 for _, s in results if s)
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n✓ All tests passed! Agent is working correctly. 🎉")
            return True
        else:
            print(f"\n✗ {total - passed} test(s) failed. Check logs above.")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Test invoice-agent HTTP endpoint",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test Function App directly
  python test_foundry_agent.py --direct
  
  # Run full test suite
  python test_foundry_agent.py
  
  # Health check only
  python test_foundry_agent.py --health
        """
    )
    
    parser.add_argument("--direct", action="store_true", 
                       help="Test Function App directly (default: full suite)")
    parser.add_argument("--health", action="store_true",
                       help="Run health check only")
    parser.add_argument("--url", default="https://invoice-agent-docintelligence2.azurewebsites.net/api/invoice",
                       help="Function App URL (default: production)")
    parser.add_argument("--resource-group", default="rmtag-openai-agents-rg",
                       help="Azure resource group")
    parser.add_argument("--function-app", default="invoice-agent-docintelligence2",
                       help="Azure Function App name")
    
    args = parser.parse_args()
    
    tester = InvoiceAgentTester(
        function_url=args.url,
        resource_group=args.resource_group,
        function_app=args.function_app
    )
    
    if args.health:
        tester.test_health_check()
    elif args.direct:
        payload = {
            "text": "Vendor: Test Corp\nInvoice #TEST-001\nAmount: $100.00"
        }
        tester.test_direct_http(payload)
    else:
        tester.run_all_tests()


if __name__ == "__main__":
    main()
