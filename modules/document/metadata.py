"""Document metadata extraction module"""

from typing import Dict
from pathlib import Path
from core.base import BaseModule
from core.exceptions import ValidationError


class MetadataExtractor(BaseModule):
    def extract(self, file_path: str) -> Dict:
        if not Path(file_path).exists():
            raise ValidationError(f"File not found: {file_path}")

        self._log_info(f"Extracting metadata from {file_path}")

        results = {
            "file": file_path,
            "metadata": {},
            "author": None,
            "created": None,
            "modified": None,
            "software": None,
            "comments": []
        }

        ext = Path(file_path).suffix.lower()

        if ext == ".pdf":
            results.update(self._extract_pdf(file_path))
        elif ext in [".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"]:
            results.update(self._extract_office(file_path))
        elif ext in [".jpg", ".jpeg", ".png", ".tiff"]:
            results.update(self._extract_image_meta(file_path))
        else:
            results.update(self._extract_generic(file_path))

        return self._format_result(True, results)

    def _extract_pdf(self, file_path: str) -> Dict:
        try:
            import PyPDF2
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)

                meta = {
                    "pages": len(reader.pages),
                    "encrypted": reader.is_encrypted
                }

                if reader.metadata:
                    meta["author"] = str(reader.metadata.get("/Author", ""))
                    meta["creator"] = str(reader.metadata.get("/Creator", ""))
                    meta["producer"] = str(reader.metadata.get("/Producer", ""))
                    meta["subject"] = str(reader.metadata.get("/Subject", ""))
                    meta["title"] = str(reader.metadata.get("/Title", ""))

                return {"metadata": meta, "software": meta.get("producer")}

        except ImportError:
            return {"metadata": {"error": "PyPDF2 not installed"}}
        except Exception as e:
            return {"metadata": {"error": str(e)}}

    def _extract_office(self, file_path: str) -> Dict:
        try:
            from pptx import Presentation
            from pptx.util import Inches

            prs = Presentation(file_path)

            meta = {
                "slides": len(prs.slides),
                "title": prs.core_properties.title,
                "author": prs.core_properties.author,
                "created": str(prs.core_properties.created),
                "modified": str(prs.core_properties.modified)
            }

            return {"metadata": meta}

        except ImportError:
            return {"metadata": {"error": "python-pptx not installed"}}
        except Exception as e:
            return {"metadata": {"error": str(e)}}

    def _extract_image_meta(self, file_path: str) -> Dict:
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS

            img = Image.open(file_path)
            exif = img._getexif()

            meta = {"width": img.width, "height": img.height, "format": img.format}

            if exif:
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    meta[tag] = str(value)

            return {"metadata": meta}

        except Exception as e:
            return {"metadata": {"error": str(e)}}

    def _extract_generic(self, file_path: str) -> Dict:
        stats = Path(file_path).stat()
        return {
            "metadata": {
                "size": stats.st_size,
                "created": stats.st_ctime,
                "modified": stats.st_mtime,
                "accessed": stats.st_atime
            }
        }