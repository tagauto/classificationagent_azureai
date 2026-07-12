import argparse
import json
import os

from invoice_agent.agent import InvoiceAgent
from invoice_agent.document_intelligence import DocumentIntelligenceService


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify and extract fields from a vendor invoice")
    parser.add_argument("input", nargs="?", default="", help="Invoice text or file path to analyze")
    args = parser.parse_args()

    agent = InvoiceAgent()

    if os.path.exists(args.input):
        service = DocumentIntelligenceService()
        result = service.analyze_invoice(args.input)
        extracted_fields = agent.extract_fields_from_document_intelligence_result(result)
    else:
        text = args.input or "Vendor: Northwind Property Services\nInvoice # 10042\nDate: 2026-07-10\nAmount Due: $1250.00"
        extracted_fields = agent.extract_fields_from_text(text)

    analysis = agent.analyze_document(extracted_fields)
    print(json.dumps({
        "extracted_fields": extracted_fields,
        "analysis": {
            "document_type": analysis.document_type,
            "confidence": analysis.confidence,
            "vendor_name": analysis.vendor_name,
            "invoice_number": analysis.invoice_number,
            "total_amount": analysis.total_amount,
            "invoice_date": analysis.invoice_date,
            "issues": [issue.message for issue in analysis.issues],
        },
    }, indent=2))


if __name__ == "__main__":
    main()
