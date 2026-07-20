import re
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
        return rows[: max(1, min(limit, 10000))]

    def print_details(self, number: str, term: int = 10) -> dict:
        return self._get(f"/term{term}/prints/{quote(number, safe='-')}")

    def process(self, number: str, term: int = 10) -> dict:
        return self._get(f"/term{term}/processes/{quote(number, safe='-')}")

    def interpellation(self, number: int, term: int = 10) -> dict:
        return self._get(f"/term{term}/interpellations/{number}")

    def committee(self, code: str, term: int = 10) -> dict:
        return self._get(f"/term{term}/committees/{quote(code, safe='')}")

    def member(self, member_id: int, term: int = 10) -> dict:
        return self._get(f"/term{term}/MP/{member_id}")

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

    @staticmethod
    def _topic_terms(topic: str) -> List[str]:
        words = [
            word.lower() for word in re.findall(r"[\w-]+", topic)
            if len(word) >= 4 or word.lower() == "ai"
        ]
        terms = set(words)
        for word in words:
            if len(word) >= 6:
                terms.add(word[:5])
        if "ai" in terms or any(word.startswith("sztucz") for word in words):
            terms.update(("ai", "sztuczn", "algorytm"))
        if any(word.startswith(("medycz", "medyc", "zdrow", "szpital")) for word in words):
            terms.update(("medycz", "zdrow", "szpital", "pacjent"))
        return sorted(terms, key=len, reverse=True)

    def search_prints(self, topic: str, term: int = 10, limit: int = 12) -> List[dict]:
        terms = self._topic_terms(topic)
        rows = self.prints(term, 10000)
        ranked = []
        for row in rows:
            title = row.get("title", "").lower()
            matches = sum(1 for value in terms if value in title)
            if matches:
                item = dict(row)
                item["_score"] = matches
                item["_url"] = f"{BASE_URL}/term{term}/prints/{quote(str(row['number']), safe='-')}"
                ranked.append(item)
        ranked.sort(
            key=lambda item: (item["_score"], item.get("deliveryDate", "")),
            reverse=True,
        )
        return ranked[:limit]

    def search_interpellations(
        self, topic: str, term: int = 10, limit: int = 8
    ) -> List[dict]:
        terms = self._topic_terms(topic)[:4]
        found = {}
        for value in terms:
            rows = self._get(
                f"/term{term}/interpellations?limit=50&sort_by=-lastModified"
                f"&title={quote(value)}"
            )
            for row in rows:
                found[row["num"]] = row
        ranked = []
        all_terms = self._topic_terms(topic)
        for row in found.values():
            title = row.get("title", "").lower()
            item = dict(row)
            item["_score"] = sum(1 for value in all_terms if value in title)
            item["_url"] = next(
                (link["href"] for link in row.get("links", [])
                 if link.get("rel") == "web-description"),
                f"{BASE_URL}/term{term}/interpellations/{row['num']}",
            )
            ranked.append(item)
        ranked.sort(
            key=lambda item: (item["_score"], item.get("receiptDate", "")),
            reverse=True,
        )
        return ranked[:limit]
