from time import monotonic
from requests import HTTPError
from .generator import generate_feeds
from api import INBOXES

begin = monotonic()

for inbox in INBOXES:
    start = monotonic()
    for language in inbox.langauges:
        
        try:
            generate_feeds(inbox, language)
        except HTTPError:
            # in case if language is not actually available
            continue

    finish = monotonic()

    print(f"Generated '{inbox.subdomain}' feeds in {finish - start:.2f}s!")

end = monotonic()

print(f"Full update took: {end - begin:.2f}s")