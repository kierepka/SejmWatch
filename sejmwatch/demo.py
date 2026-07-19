from pathlib import Path

from .db import init_db
from .diffing import compare_documents
from .ingest import import_document


V1 = [
    "PROJEKT USTAWY O ODPORNOŚCI CYFROWEJ\n\nArt. 1. Ustawa określa obowiązki podmiotów leczniczych w zakresie bezpieczeństwa systemów informacyjnych.",
    "Art. 14. 1. Podmiot leczniczy zgłasza poważny incydent właściwemu organowi.\n2. Okres dostosowawczy wynosi 24 miesiące od dnia wejścia ustawy w życie.",
    "Art. 20. Ustawa wchodzi w życie po upływie 30 dni od dnia ogłoszenia.",
]

V2 = [
    "PROJEKT USTAWY O ODPORNOŚCI CYFROWEJ\n\nArt. 1. Ustawa określa obowiązki podmiotów leczniczych oraz dostawców ich systemów IT w zakresie bezpieczeństwa systemów informacyjnych.",
    "Art. 14. 1. Podmiot leczniczy zgłasza poważny incydent właściwemu organowi nie później niż w ciągu 24 godzin od jego wykrycia.\n2. Okres dostosowawczy wynosi 12 miesięcy od dnia wejścia ustawy w życie.",
    "Art. 15. Dostawca systemu IT prowadzi rejestr incydentów i udostępnia go podmiotowi leczniczemu na żądanie.\n\nArt. 20. Ustawa wchodzi w życie po upływie 30 dni od dnia ogłoszenia.",
]


def seed(db_path: str) -> None:
    init_db(db_path)
    import_document(
        db_path, "cyber-health", "Odporność cyfrowa ochrony zdrowia",
        "druk-demo-v1", "Wersja pierwotna", "https://www.sejm.gov.pl/Sejm10.nsf/druki.xsp",
        "\f".join(V1).encode(), pages=V1,
    )
    import_document(
        db_path, "cyber-health", "Odporność cyfrowa ochrony zdrowia",
        "druk-demo-v2", "Wersja po komisji", "https://www.sejm.gov.pl/Sejm10.nsf/druki.xsp",
        "\f".join(V2).encode(), pages=V2,
    )
    compare_documents(db_path, "druk-demo-v1", "druk-demo-v2")


if __name__ == "__main__":
    seed(str(Path("data/sejmwatch.db")))
    print("Demo dataset loaded.")

