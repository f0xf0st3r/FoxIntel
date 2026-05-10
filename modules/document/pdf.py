"""PDF analysis module"""

from typing import Dict, List
from pathlib import Path
from core.base import BaseModule
from core.exceptions import ValidationError


class PDFAnalyzer(BaseModule):
    def analyze(self, file_path: str) -> Dict:
        if not Path(file_path).exists():
            raise ValidationError(f"File not found: {file_path}")

        self._log_info(f"Analyzing PDF: {file_path}")

        results = {
            "file": file_path,
            "pages": 0,
            "text": [],
            "urls": [],
            "attachments": [],
            "metadata": {},
            "security": {}
        }

        try:
            import PyPDF2

            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)

                results["pages"] = len(reader.pages)
                results["encrypted"] = reader.is_encrypted

                if reader.metadata:
                    results["metadata"] = {
                        "author": str(reader.metadata.get("/Author", "")),
                        "creator": str(reader.metadata.get("/Creator", "")),
                        "producer": str(reader.metadata.get("/Producer", "")),
                        "subject": str(reader.metadata.get("/Subject", "")),
                        "title": str(reader.metadata.get("/Title", "")),
                    }

                for page_num, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text:
                        results["text"].append({
                            "page": page_num + 1,
                            "content": text[:1000]
                        })

                    urls = self._extract_urls(text)
                    results["urls"].extend(urls)

                results["security"] = self._check_security(reader)

        except ImportError:
            results["error"] = "PyPDF2 not installed"
        except Exception as e:
            results["error"] = str(e)

        return self._format_result(True, results)

    def _extract_urls(self, text: str) -> List[str]:
        import re
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return list(set(re.findall(url_pattern, text)))

    def _check_security(self, reader) -> Dict:
        return {
            "encrypted": reader.is_encrypted,
            "extractable": True
        }