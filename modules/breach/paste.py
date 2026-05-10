"""Paste site searcher module"""

from typing import Dict
from core.base import BaseModule
from core.utils import validate_email
from core.exceptions import ValidationError


class PasteSearcher(BaseModule):
    PASTE_SITES = [
        "pastebin.com",
        "pastie.org",
        "slexy.org",
        " hastebin.com",
        "ghostbin.com",
        "dpaste.org",
    ]

    def search(self, email: str) -> Dict:
        if not validate_email(email):
            raise ValidationError(f"Invalid email: {email}")

        self._log_info(f"Paste site search for {email}")

        results = {
            "email": email,
            "paste_sites": self.PASTE_SITES,
            "found_pastes": [],
            "search_urls": []
        }

        for site in self.PASTE_SITES:
            results["search_urls"].append(f"https://{site}/search?q={email}")

        return self._format_result(True, results)