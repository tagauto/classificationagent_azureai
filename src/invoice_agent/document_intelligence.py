import os
from typing import Any, Dict, Optional

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest


class DocumentIntelligenceService:
    def __init__(self, endpoint: Optional[str] = None, key: Optional[str] = None) -> None:
        endpoint = endpoint or os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
        key = key or os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")

        if not endpoint or not key:
            raise ValueError(
                "Set AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT and AZURE_DOCUMENT_INTELLIGENCE_KEY before using the service."
            )

        self.client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    def analyze_invoice(self, file_path: str) -> Dict[str, Any]:
        with open(file_path, "rb") as f:
            poller = self.client.begin_analyze_document(
                "prebuilt-invoice",
                AnalyzeDocumentRequest(bytes_source=f.read()),
                content_type="application/octet-stream",
            )
        return poller.result().as_dict()
