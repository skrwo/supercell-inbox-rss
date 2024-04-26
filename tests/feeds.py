from pathlib import Path
from json import loads
from feed.generator import generate_feed, save_feed
from api import INBOXES
from time import monotonic
from os import remove, removedirs

def test_feedgen():
    begin = monotonic()
    mock_path = Path("./mock")
    
    for inbox in INBOXES:
        start = monotonic()
        path = mock_path / inbox.subdomain
        if not path.exists():
            print(f"no '{inbox.subdomain}' mock files! Run 'python -m mock'")
            continue
        for file in path.iterdir():
            json = file.read_text()
            data = loads(json)

            for key in {
                "eventEntries",
                "newsEntries",
                "communityEntries",
                "esportNewsEntries",
            }:
                if key in data.get("entries", {}):
                    for language in inbox.langauges:
                        filename = key.removesuffix("Entries")
                        feed = generate_feed(inbox, f"mock-{language}", key, data)
                        try:
                            save_feed(feed, inbox.subdomain, f"mock-{language}", filename)
                        except ValueError as e:
                            print("[!] failed to save", inbox.subdomain, language, key)
                            print("error", e)
                            continue
                        
                        remove((f"./rss/{inbox.subdomain}/mock-{language}/{filename}.xml"))
                        remove((f"./rss/{inbox.subdomain}/mock-{language}/{filename}.atom"))
                
                for file in Path(f"./rss/{inbox.subdomain}").iterdir():
                    if file.is_dir() and file.name.startswith("mock"):
                        try:
                            removedirs((file))
                        except Exception as e:
                            print(e)

        finish = monotonic()
        print(f"Mocked '{inbox.subdomain}' feed generation took {finish - start:.2f}s!")

    end = monotonic()
    print(f"Feed generations from mocked data took {end - begin:.2f}s!")
