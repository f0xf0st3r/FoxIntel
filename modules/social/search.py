"""Social media search module"""

import json
from typing import Dict, List
from core.base import BaseModule


class SocialSearcher(BaseModule):
    PLATFORMS = {
        "twitter": "https://twitter.com/search?q=",
        "instagram": "https://instagram.com/",
        "linkedin": "https://www.linkedin.com/search/results/all/?keywords=",
        "facebook": "https://www.facebook.com/search/top/?q=",
        "github": "https://github.com/search?q=",
    }

    def search(self, query: str, platform: str = "all") -> Dict:
        self._log_info(f"Social media search: {query} on {platform}")

        results = {
            "query": query,
            "platform": platform,
            "profiles": [],
            "posts": []
        }

        if platform == "all":
            for p in self.PLATFORMS:
                results["profiles"].extend(self._search_platform(query, p))
        else:
            results["profiles"] = self._search_platform(query, platform)

        return self._format_result(True, results)

    def _search_platform(self, query: str, platform: str) -> List[Dict]:
        profiles = []
        url = self.PLATFORMS.get(platform, "")

        profiles.append({
            "platform": platform,
            "query": query,
            "search_url": f"{url}{query}",
            "note": "Manual review may be required"
        })

        return profiles