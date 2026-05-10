"""Coordinate intelligence analysis module"""

from typing import Dict
from core.base import BaseModule


class CoordinateIntelligence(BaseModule):
    def analyze(self, latitude: float, longitude: float) -> Dict:
        self._log_info(f"Analyzing coordinates: {latitude}, {longitude}")

        results = {
            "coordinates": {
                "latitude": latitude,
                "longitude": longitude
            },
            "location_info": {},
            "nearby_places": [],
            "timezone": {},
            "satellite": {}
        }

        results["location_info"] = self._reverse_geocode(latitude, longitude)
        results["nearby_places"] = self._find_nearby(latitude, longitude)
        results["timezone"] = self._get_timezone(latitude, longitude)

        return self._format_result(True, results)

    def _reverse_geocode(self, lat: float, lon: float) -> Dict:
        try:
            response = self.http.get(
                f"https://nominatim.openstreetmap.org/reverse",
                params={"lat": lat, "lon": lon, "format": "json"}
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "address": data.get("display_name"),
                    "type": data.get("type"),
                    "category": data.get("category"),
                    "country": data.get("address", {}).get("country"),
                    "city": data.get("address", {}).get("city"),
                    "state": data.get("address", {}).get("state")
                }
        except:
            pass

        return {}

    def _find_nearby(self, lat: float, lon: float) -> list:
        nearby = []
        categories = ["restaurant", "hotel", "school", "hospital", "airport"]

        for cat in categories[:3]:
            try:
                response = self.http.get(
                    "https://overpass-api.de/api/interpreter",
                    params={
                        "data": f"""
                        [out:json];
                        node["amenity"="{cat}"](around:1000,{lat},{lon});
                        out;
                        """
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    for element in data.get("elements", [])[:5]:
                        nearby.append({
                            "type": cat,
                            "name": element.get("tags", {}).get("name"),
                            "distance": "unknown"
                        })
            except:
                pass

        return nearby

    def _get_timezone(self, lat: float, lon: float) -> Dict:
        try:
            response = self.http.get(
                "http://api.geonames.org/timezoneJSON",
                params={"lat": lat, "lng": lon, "username": "foxintel"}
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "timezone": data.get("timezone"),
                    "gmt_offset": data.get("gmtOffset"),
                    "dst_offset": data.get("dstOffset")
                }
        except:
            pass

        return {}