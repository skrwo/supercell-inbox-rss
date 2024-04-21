from api import INBOXES, AVAILABLE_LANGUAGES
from requests.exceptions import HTTPError


def test_api_endpoints():
    r = lambda x: "ok" if x else "fail"

    lang = "en"

    print("== API endpoints test ==")

    for inbox in INBOXES:
        print("testing", inbox.subdomain)

        news = inbox.get_news(lang)
        print("/news", r(news))

        community = inbox.get_community(lang)
        print("/community", r(community))

        esport = inbox.get_esport(lang)
        print("/esport", r(esport), "\n")


def test_available_languages():
    unavailable = AVAILABLE_LANGUAGES.copy()
    print("== Available languages test ==")
    for inbox in INBOXES:
        available = set()
        for lang in AVAILABLE_LANGUAGES:
            try:
                inbox.get_news(lang)
                if lang in unavailable:
                    unavailable.remove(lang)
                available.add(lang)
            except HTTPError:
                pass
        print(f"'{inbox.subdomain}' available languages: {available}")
    print(f"Unavailable languages: {unavailable}")