from typing import List, Optional
from urllib.parse import quote

import httpx


BASE_URL = "https://api.sejm.gov.pl/sejm"


class SejmAPI:
    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout

    def _get(self, path: str):
        response = httpx.get(
            f"{BASE_URL}{path}",
            headers={"Accept": "application/json", "User-Agent": "SejmWatch/0.1"},
            timeout=self.timeout,
            follow_redirects=True,
        )
        response.raise_for_status()
        return response.json()

    def term(self, term: int = 10) -> dict:
        return self._get(f"/term{term}")

    def prints(self, term: int = 10, limit: int = 30) -> List[dict]:
        # The API currently returns the complete list; truncate locally to keep
        # rendering and memory predictable on a small Heroku dyno.
        rows = self._get(f"/term{term}/prints?sort_by=-deliveryDate")
        return rows[: max(1, min(limit, 100))]

    def print_details(self, number: str, term: int = 10) -> dict:
        return self._get(f"/term{term}/prints/{quote(number, safe='-')}")

    def process(self, number: str, term: int = 10) -> dict:
        return self._get(f"/term{term}/processes/{quote(number, safe='-')}")

    def interpellation(self, number: int, term: int = 10) -> dict:
        return self._get(f"/term{term}/interpellations/{number}")

    @staticmethod
    def attachment_url(term: int, number: str, attachment: str) -> str:
        return (
            f"{BASE_URL}/term{term}/prints/"
            f"{quote(number, safe='-')}/{quote(attachment, safe='-.')}"
        )

    def primary_pdf(self, details: dict) -> Optional[str]:
        for attachment in details.get("attachments", []):
            if attachment.lower().endswith(".pdf"):
                return self.attachment_url(
                    int(details["term"]), str(details["number"]), attachment
                )
        return None
