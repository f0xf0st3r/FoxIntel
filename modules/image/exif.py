"""EXIF metadata extraction module"""

from typing import Dict
from pathlib import Path
from core.base import BaseModule
from core.exceptions import ValidationError


class EXIFExtractor(BaseModule):
    def extract(self, image_path: str) -> Dict:
        if not Path(image_path).exists():
            raise ValidationError(f"File not found: {image_path}")

        self._log_info(f"EXIF extraction from {image_path}")

        results = {
            "file": image_path,
            "exif_data": {},
            "gps_data": {},
            "camera_info": {},
            "timestamp": None
        }

        try:
            from PIL import Image
            from PIL.ExifTags import TAGS, GPSTAGS

            img = Image.open(image_path)
            exif = img._getexif()

            if exif:
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)

                    if tag in ("GPSInfo", "GPS GPSInfo"):
                        gps_data = {}
                        for gps_tag in value:
                            gps_tag_name = GPSTAGS.get(gps_tag, gps_tag)
                            gps_data[gps_tag_name] = value[gps_tag]
                        results["gps_data"] = gps_data
                    elif tag in ("DateTime", "DateTimeOriginal", "DateTimeDigitized"):
                        results["timestamp"] = value
                    elif tag in ("Make", "Model", "Software", "LensModel", "FocalLength"):
                        results["camera_info"][tag] = value
                    else:
                        results["exif_data"][tag] = str(value)

            results["image_info"] = {
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "mode": img.mode
            }

        except ImportError:
            results["error"] = "PIL not installed. Install with: pip install Pillow"
        except Exception as e:
            results["error"] = str(e)

        return self._format_result(True, results)