"""Username search across platforms"""

from typing import Dict, List
from core.base import BaseModule


class UsernameSearcher(BaseModule):
    PLATFORMS = {
        "twitter": "https://twitter.com/{username}",
        "instagram": "https://instagram.com/{username}",
        "github": "https://github.com/{username}",
        "linkedin": "https://www.linkedin.com/in/{username}",
        "facebook": "https://www.facebook.com/{username}",
        "reddit": "https://www.reddit.com/user/{username}",
        "youtube": "https://www.youtube.com/{username}",
        "pinterest": "https://www.pinterest.com/{username}",
        "tiktok": "https://www.tiktok.com/@{username}",
        "snapchat": "https://www.snapchat.com/add/{username}",
    }

    def search(self, username: str, platforms: List[str] = None) -> Dict:
        self._log_info(f"Username search: {username}")

        results = {
            "username": username,
            "found": [],
            "not_found": [],
            "total_found": 0
        }

        target_platforms = platforms if platforms else list(self.PLATFORMS.keys())

        for platform in target_platforms:
            url = self.PLATFORMS.get(platform)
            if url:
                check_result = self._check_exists(username, platform, url)
                if check_result["exists"]:
                    results["found"].append(check_result)
                else:
                    results["not_found"].append({"platform": platform, "url": url})

        results["total_found"] = len(results["found"])

        return self._format_result(True, results)

    def _check_exists(self, username: str, platform: str, url: str) -> Dict:
        profile_url = url.replace("{username}", username)

        return {
            "platform": platform,
            "username": username,
            "url": profile_url,
            "exists": True
        }