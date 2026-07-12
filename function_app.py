import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

import azure.functions as func

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from invoice_agent.agent import InvoiceAgent
from invoice_agent.document_intelligence import DocumentIntelligenceService


app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.function_name(name="invoiceprocessor")
@app.route(route="invoice", methods=["POST"])
def invoiceprocessor(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_body()
        if not body:
            return func.HttpResponse("Request body is required", status_code=400)

        payload = json.loads(body)
        file_path = payload.get("file_path")
        text = payload.get("text")

        agent = InvoiceAgent()
        if file_path:
            service = DocumentIntelligenceService()
            di_result = service.analyze_invoice(file_path)
            extracted_fields = agent.extract_fields_from_document_intelligence_result(di_result)
        elif text:
            extracted_fields = agent.extract_fields_from_text(text)
        else:
            return func.HttpResponse("Provide either file_path or text", status_code=400)

        analysis = agent.analyze_document(extracted_fields)
        response = {
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
        }
        return func.HttpResponse(json.dumps(response), mimetype="application/json", status_code=200)
    except Exception as exc:  # pragma: no cover - defensive path
        return func.HttpResponse(json.dumps({"error": str(exc)}), mimetype="application/json", status_code=500)
