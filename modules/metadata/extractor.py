"""Generic metadata extractor module"""

from typing import Dict
from pathlib import Path
from core.base import BaseModule
from core.exceptions import ValidationError


class GenericMetadataExtractor(BaseModule):
    def extract(self, file_path: str) -> Dict:
        if not Path(file_path).exists():
            raise ValidationError(f"File not found: {file_path}")

        self._log_info(f"Extracting metadata from: {file_path}")

        results = {
            "file": file_path,
            "file_info": {},
            "metadata": {},
            "embedded_data": {}
        }

        results["file_info"] = self._get_file_info(file_path)
        results["metadata"] = self._extract_meta(file_path)
        results["embedded_data"] = self._find_embedded(file_path)

        return self._format_result(True, results)

    def _get_file_info(self, file_path: str) -> Dict:
        import os
        stats = os.stat(file_path)

        return {
            "name": Path(file_path).name,
            "extension": Path(file_path).suffix,
            "size": stats.st_size,
            "created": stats.st_ctime,
            "modified": stats.st_mtime,
            "permissions": oct(stats.st_mode)[-3:]
        }

    def _extract_meta(self, file_path: str) -> Dict:
        meta = {}
        ext = Path(file_path).suffix.lower()

        if ext == ".pdf":
            meta = self._extract_pdf_meta(file_path)
        elif ext in [".jpg", ".jpeg", ".png", ".gif", ".tiff"]:
            meta = self._extract_image_meta(file_path)
        elif ext in [".doc", ".docx", ".xls", ".xlsx", ".ppt"]:
            meta = self._extract_office_meta(file_path)
        elif ext == ".mp3":
            meta = self._extract_audio_meta(file_path)
        elif ext in [".mp4", ".avi", ".mov"]:
            meta = self._extract_video_meta(file_path)

        return meta

    def _extract_pdf_meta(self, file_path: str) -> Dict:
        meta = {}
        try:
            import PyPDF2
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                if reader.metadata:
                    meta = {
                        "author": str(reader.metadata.get("/Author", "")),
                        "creator": str(reader.metadata.get("/Creator", "")),
                        "producer": str(reader.metadata.get("/Producer", "")),
                        "title": str(reader.metadata.get("/Title", ""))
                    }
        except:
            pass
        return meta

    def _extract_image_meta(self, file_path: str) -> Dict:
        meta = {}
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS

            img = Image.open(file_path)
            meta = {"format": img.format, "size": f"{img.width}x{img.height}"}

            if hasattr(img, '_getexif') and img._getexif():
                for tag_id, value in img._getexif().items():
                    tag = TAGS.get(tag_id, tag_id)
                    meta[tag] = str(value)
        except:
            pass
        return meta

    def _extract_office_meta(self, file_path: str) -> Dict:
        meta = {}
        try:
            from docx import Document
            doc = Document(file_path)
            core = doc.core_properties
            meta = {
                "author": core.author,
                "created": str(core.created),
                "modified": str(core.modified),
                "title": core.title
            }
        except:
            pass
        return meta

    def _extract_audio_meta(self, file_path: str) -> Dict:
        return {"format": Path(file_path).suffix}

    def _extract_video_meta(self, file_path: str) -> Dict:
        return {"format": Path(file_path).suffix}

    def _find_embedded(self, file_path: str) -> Dict:
        embedded = {"found": False, "items": []}

        try:
            with open(file_path, "rb") as f:
                content = f.read()

                strings = []
                current = b""
                for byte in content:
                    if 32 <= byte <= 126:
                        current += bytes([byte])
                    else:
                        if len(current) > 8:
                            strings.append(current.decode("utf-8", errors="ignore"))
                        current = b""

                embedded["found"] = len(strings) > 0
                embedded["strings_count"] = len(strings)

        except:
            pass

        return embedded