import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Issue:
    message: str

    def __str__(self) -> str:
        return self.message


@dataclass
class AnalysisResult:
    document_type: str
    confidence: float
    vendor_name: Optional[str] = None
    invoice_number: Optional[str] = None
    total_amount: Optional[float] = None
    invoice_date: Optional[str] = None
    issues: List[Issue] = field(default_factory=list)


class InvoiceAgent:
    """Simple invoice extraction and classification agent for local prototyping."""

    def analyze_document(self, extracted_fields: Dict[str, Any]) -> AnalysisResult:
        vendor_name = (extracted_fields.get("vendor_name") or "").strip()
        invoice_number = (extracted_fields.get("invoice_number") or "").strip()
        total_amount = extracted_fields.get("total_amount")
        invoice_date = (extracted_fields.get("invoice_date") or "").strip()

        issues: List[Issue] = []
        score = 0.0

        if vendor_name:
            score += 0.3
        else:
            issues.append(Issue("Missing vendor name."))

        if invoice_number:
            score += 0.3
        else:
            issues.append(Issue("Missing invoice number."))

        if total_amount is not None:
            score += 0.2
        else:
            issues.append(Issue("Missing total amount."))

        if invoice_date:
            score += 0.2
        else:
            issues.append(Issue("Missing invoice date."))

        if score >= 0.8:
            document_type = "vendor_invoice"
            confidence = min(0.99, 0.75 + score * 0.2)
        else:
            document_type = "unknown_document"
            confidence = round(max(0.1, score), 2)
            issues.insert(0, Issue("Missing invoice identifiers."))

        return AnalysisResult(
            document_type=document_type,
            confidence=confidence,
            vendor_name=vendor_name or None,
            invoice_number=invoice_number or None,
            total_amount=float(total_amount) if total_amount is not None else None,
            invoice_date=invoice_date or None,
            issues=issues,
        )

    def extract_fields_from_text(self, text: str) -> Dict[str, Any]:
        cleaned_text = text.replace("\\n", "\n")
        lines = [line.strip() for line in cleaned_text.splitlines() if line.strip()]
        vendor_name = None
        invoice_number = None
        total_amount = None

        for line in lines:
            if vendor_name is None and re.search(r"\bvendor\b", line, re.IGNORECASE):
                vendor_match = re.search(r"vendor[:\s]+(.+)", line, re.IGNORECASE)
                if vendor_match:
                    vendor_name = vendor_match.group(1).strip()
                    break

        for line in lines:
            invoice_match = re.search(r"invoice\s*#?\s*(\d+[A-Za-z0-9-]*)", line, re.IGNORECASE)
            if invoice_match:
                invoice_number = invoice_match.group(1).strip()
                break

        for line in lines:
            if re.search(r"\b(amount|total|due)\b", line, re.IGNORECASE):
                amount_match = re.search(r"\$?([0-9,]+(?:\.\d{1,2})?)", line)
                if amount_match:
                    total_amount = float(amount_match.group(1).replace(",", ""))
                    break

        return {
            "vendor_name": vendor_name,
            "invoice_number": invoice_number,
            "total_amount": total_amount,
            "invoice_date": None,
        }

    def extract_fields_from_document_intelligence_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        fields = {}
        for page in result.get("pages", []):
            for key, value in page.get("fields", {}).items():
                if not isinstance(value, dict):
                    continue

                if "value_string" in value:
                    fields[key] = value["value_string"]
                elif "value_currency" in value:
                    fields[key] = value["value_currency"].get("amount")
                elif "value_date" in value:
                    fields[key] = value["value_date"]

        vendor_name = self._get_field_value(fields, ["VendorName", "vendor_name", "Vendor"])
        invoice_number = self._get_field_value(fields, ["InvoiceId", "invoice_id", "InvoiceNumber", "invoice_number"])
        total_amount = self._get_field_value(fields, ["AmountDue", "amount_due", "TotalAmount", "total_amount"])
        invoice_date = self._get_field_value(fields, ["InvoiceDate", "invoice_date", "Date"])

        return {
            "vendor_name": vendor_name,
            "invoice_number": invoice_number,
            "total_amount": total_amount,
            "invoice_date": invoice_date,
        }

    def _get_field_value(self, fields: Dict[str, Any], keys: List[str]) -> Optional[Any]:
        for key in keys:
            if key in fields and fields[key] is not None:
                return fields[key]
        return None
