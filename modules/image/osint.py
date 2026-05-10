"""Image reverse image search OSINT"""

from typing import Dict
from pathlib import Path
from core.base import BaseModule
from core.exceptions import ValidationError


class ImageOSINT(BaseModule):
    SEARCH_ENGINES = {
        "google": "https://www.google.com/searchbyimage?image_url=",
        "yandex": "https://yandex.com/images/search?rpt=imageview&url=",
        "bing": "https://www.bing.com/images/search?q=imgurl:",
        "tineye": "https://www.tineye.com/search?url=",
        "yahoo": "https://images.search.yahoo.com/search/images?p=",
    }

    def search(self, image_path: str) -> Dict:
        self._log_info(f"Image OSINT for {image_path}")

        results = {
            "input": image_path,
            "hash": None,
            "search_urls": [],
            "similar_images": []
        }

        if image_path.startswith("http"):
            results["type"] = "url"
            results["url"] = image_path
        else:
            path = Path(image_path)
            if not path.exists():
                raise ValidationError(f"File not found: {image_path}")
            results["type"] = "local"
            results["file"] = image_path

        results["search_urls"] = self._generate_search_urls(image_path)
        results["hash"] = self._calculate_perceptual_hash(image_path)

        return self._format_result(True, results)

    def _generate_search_urls(self, image: str) -> Dict[str, str]:
        import urllib.parse
        encoded = urllib.parse.quote(image)
        return {name: url + encoded for name, url in self.SEARCH_ENGINES.items()}

    def _calculate_perceptual_hash(self, image: str) -> str:
        try:
            import imagehash
            from PIL import Image

            if image.startswith("http"):
                import urllib.request
                import io
                with urllib.request.urlopen(image) as response:
                    img = Image.open(io.BytesIO(response.read()))
            else:
                img = Image.open(image)

            phash = str(imagehash.phash(img))
            ahash = str(imagehash.average_hash(img))
            dhash = str(imagehash.dhash(img))
            whash = str(imagehash.whash(img))

            return {
                "phash": phash,
                "ahash": ahash,
                "dhash": dhash,
                "whash": whash
            }
        except ImportError:
            import hashlib
            with open(image, "rb") as f:
                return {"md5": hashlib.md5(f.read()).hexdigest()}
        except:
            return None