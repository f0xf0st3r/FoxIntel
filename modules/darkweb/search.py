"""Dark web search module"""

from typing import Dict, List
from core.base import BaseModule


class DarkWebSearcher(BaseModule):
    SEARCH_ENGINES = [
        "http://grams7enufi7jdb6.onion",
        "http://darksearchfrl.onion",
        "http://torepda3lg53wmrj.onion",
    ]

    def search(self, query: str) -> Dict:
        self._log_info(f"Dark web search for: {query}")

        results = {
            "query": query,
            "tor_available": self._check_tor(),
            "engines": self.SEARCH_ENGINES,
            "results": [],
            "warnings": []
        }

        if not self._check_tor():
            results["warnings"].append("Tor not detected - dark web access may be limited")

        results["onion_links"] = self._search_onion_sites(query)

        return self._format_result(True, results)

    def _check_tor(self) -> bool:
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex(("127.0.0.1", 9050))
            sock.close()
            return result == 0
        except:
            return False

    def _search_onion_sites(self, query: str) -> List[Dict]:
        links = []

        onion_sites = {
            "ahmia": f"http://ahmia.fi/search/?q={query}",
            "darksearch": f"http://darksearchfrl.onion/search?q={query}",
        }

        for name, url in onion_sites.items():
            links.append({
                "engine": name,
                "search_url": url,
                "note": "Requires Tor browser"
            })

        return links