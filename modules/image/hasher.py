"""Image hash calculation module"""

import hashlib
from typing import Dict
from pathlib import Path
from core.base import BaseModule
from core.exceptions import ValidationError


class ImageHasher(BaseModule):
    def hash(self, image_path: str) -> Dict:
        if not Path(image_path).exists():
            raise ValidationError(f"File not found: {image_path}")

        self._log_info(f"Calculating hashes for {image_path}")

        results = {
            "file": image_path,
            "size_bytes": Path(image_path).stat().st_size,
            "hashes": {}
        }

        with open(image_path, "rb") as f:
            data = f.read()

        results["hashes"]["md5"] = hashlib.md5(data).hexdigest()
        results["hashes"]["sha1"] = hashlib.sha1(data).hexdigest()
        results["hashes"]["sha256"] = hashlib.sha256(data).hexdigest()

        try:
            import imagehash
            from PIL import Image

            img = Image.open(image_path)

            results["hashes"]["ahash"] = str(imagehash.average_hash(img))
            results["hashes"]["phash"] = str(imagehash.phash(img))
            results["hashes"]["dhash"] = str(imagehash.dhash(img))
            results["hashes"]["whash"] = str(imagehash.whash(img))

            results["perceptual_hashes"] = True

        except ImportError:
            results["perceptual_hashes"] = False
            results["hashes"]["note"] = "Install imagehash for perceptual hashes"
        except Exception as e:
            results["perceptual_hash_error"] = str(e)

        return self._format_result(True, results)