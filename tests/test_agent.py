import pytest

from invoice_agent.agent import InvoiceAgent


def test_classifies_real_vendor_invoice():
    agent = InvoiceAgent()
    result = agent.analyze_document(
        extracted_fields={
            "vendor_name": "Northwind Property Services",
            "invoice_number": "INV-10042",
            "total_amount": 1250.0,
            "invoice_date": "2026-07-10",
        }
    )

    assert result.document_type == "vendor_invoice"
    assert result.confidence >= 0.8
    assert result.vendor_name == "Northwind Property Services"
    assert result.total_amount == 1250.0


def test_flags_non_invoice_documents():
    agent = InvoiceAgent()
    result = agent.analyze_document(
        extracted_fields={
            "vendor_name": "",
            "invoice_number": "",
            "total_amount": None,
            "invoice_date": "",
        }
    )

    assert result.document_type == "unknown_document"
    assert result.confidence < 0.6
    assert "missing invoice identifiers" in str(result.issues[0]).lower()


def test_extracts_fields_from_inline_text():
    agent = InvoiceAgent()
    result = agent.extract_fields_from_text(
        "Vendor: Skyline Maintenance\nInvoice # 8841\nDate: 2026-07-01\nAmount Due: $980.00"
    )

    assert result["vendor_name"] == "Skyline Maintenance"
    assert result["invoice_number"] == "8841"
    assert result["total_amount"] == 980.0


def test_extracts_fields_from_document_intelligence_payload():
    agent = InvoiceAgent()
    result = agent.extract_fields_from_document_intelligence_result(
        {
            "pages": [
                {
                    "fields": {
                        "VendorName": {"value_string": "Northwind Property Services"},
                        "InvoiceId": {"value_string": "INV-10042"},
                        "AmountDue": {"value_currency": {"amount": 1250.0}},
                        "InvoiceDate": {"value_date": "2026-07-10"},
                    }
                }
            ]
        }
    )

    assert result["vendor_name"] == "Northwind Property Services"
    assert result["invoice_number"] == "INV-10042"
    assert result["total_amount"] == 1250.0
    assert result["invoice_date"] == "2026-07-10"


def test_function_app_imports():
    import function_app

    assert function_app.app is not None
