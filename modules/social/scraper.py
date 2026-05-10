"""Profile scraping module"""

from typing import Dict
from core.base import BaseModule


class ProfileScraper(BaseModule):
    PLATFORM_HANDLERS = {
        "twitter": "_scrape_twitter",
        "instagram": "_scrape_instagram",
        "github": "_scrape_github",
        "linkedin": "_scrape_linkedin",
    }

    def scrape(self, platform: str, username: str) -> Dict:
        self._log_info(f"Scraping {platform} profile: {username}")

        results = {
            "platform": platform,
            "username": username,
            "profile_data": {},
            "posts": [],
            "metadata": {}
        }

        handler = self.PLATFORM_HANDLERS.get(platform.lower())
        if handler:
            results["profile_data"] = getattr(self, handler)(username)

        return self._format_result(True, results)

    def _scrape_twitter(self, username: str) -> Dict:
        return {
            "url": f"https://twitter.com/{username}",
            "platform": "Twitter",
            "note": "Requires authentication for full data"
        }

    def _scrape_instagram(self, username: str) -> Dict:
        return {
            "url": f"https://instagram.com/{username}",
            "platform": "Instagram",
            "note": "Requires authentication for full data"
        }

    def _scrape_github(self, username: str) -> Dict:
        try:
            response = self.http.get(f"https://api.github.com/users/{username}")
            if response.status_code == 200:
                data = response.json()
                return {
                    "login": data.get("login"),
                    "name": data.get("name"),
                    "company": data.get("company"),
                    "blog": data.get("blog"),
                    "location": data.get("location"),
                    "bio": data.get("bio"),
                    "public_repos": data.get("public_repos"),
                    "public_gists": data.get("public_gists"),
                    "followers": data.get("followers"),
                    "following": data.get("following"),
                    "created_at": data.get("created_at"),
                    "avatar_url": data.get("avatar_url")
                }
        except:
            pass

        return {"error": "Could not fetch GitHub profile"}

    def _scrape_linkedin(self, username: str) -> Dict:
        return {
            "url": f"https://linkedin.com/in/{username}",
            "platform": "LinkedIn",
            "note": "Requires authentication"
        }