from requests import Session, Timeout
from typing import Literal


class SupercellInbox:
    """Wrapper for Supercell's Inbox API (officially it's not open)"""

    def __init__(
        self,
        subdomain: str,
        endpoints: set[Literal["news", "community", "esport"]],
        langauges: set[str],
    ) -> None:
        self.subdomain = subdomain
        self.endpoints = endpoints
        self.langauges = langauges

        self.requests = Session()
        self.requests.headers = {"user-agent": "github.com/skrwo/supercell-inbox-rss"}

    def _get_json(self, endpoint: str, language: str) -> dict:
        assert (
            endpoint in self.endpoints
        ), f"endpoint '{endpoint}' is not supported in '{self.subdomain}.inbox.supercell.com'"

        url = f"https://{self.subdomain}.inbox.supercell.com/data/{language}/{endpoint}/content.json"

        r = self.requests.get(url)
        r.raise_for_status()

        return r.json()

    def _get_endpoint(self, endpoint: str, language: str) -> dict | None:
        if endpoint not in self.endpoints:
            return None
        return self._get_json(endpoint, language)

    def compose_resource_url(self, url: str) -> str:
        url = url.removeprefix("/")
        return f"https://{self.subdomain}.inbox.supercell.com/{url}"

    def get_resource_length(self, url: str) -> int | None:
        try:
            r = self.requests.head(url, timeout=2)
            if not r.ok:
                return None
            return int(r.headers["content-length"])
        except Timeout:
            return None

    def get_news(self, language: str) -> dict | None:
        return self._get_endpoint("news", language)

    def get_community(self, language: str) -> dict | None:
        return self._get_endpoint("community", language)

    def get_esport(self, language: str) -> dict | None:
        return self._get_endpoint("esport", language)


INBOXES = [
    SupercellInbox(
        "brawlstars",
        {"news", "community", "esport"},
        {"fr", "de", "ja", "id", "ru", "ko", "es", "tr", "zh", "pt", "it", "pl", "en"},
    ),
    SupercellInbox(
        "clashroyale",
        {"news", "community", "esport"},
        {"fr", "de", "ja", "id", "ru", "ko", "es", "zh", "th", "it", "pt", "en"},
    ),
    SupercellInbox(
        "clashofclans",
        {"news", "community", "esport"},
        {"fr", "de", "ja", "id", "ko", "es", "tr", "zh", "pt", "it", "en"},
    ),
    SupercellInbox(
        "hayday",
        {"news", "community"},
        {
            "ar",
            "fr",
            "de",
            "ja",
            "fi",
            "id",
            "ru",
            "ko",
            "es",
            "tr",
            "zh",
            "nl",
            "th",
            "it",
            "pt",
            "ms",
            "en",
        },
    ),
    SupercellInbox("boombeach", {"news", "community"}, {"en"}),
    SupercellInbox("clashmini", {"news"}, {"es", "en"}),
    SupercellInbox(
        "squadbusters",
        {"news"},
        {"fr", "de", "ja", "ru", "ko", "es", "tr", "zh", "pt", "it", "pl", "en"},
    ),
]

AVAILABLE_LANGUAGES = {
    "en",
    "ar",
    "de",
    "es",
    "fi",
    "fr",
    "id",
    "it",
    "ja",
    "ko",
    "ms",
    "nl",
    "pl",
    "pt",
    "ru",
    "th",
    "tr",
    "zh",
}
