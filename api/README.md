# Supercell Inbox API
Here we have an API wrapper for Supercell Inbox API (which is actually a regular S3 bucket?), using Python `requests` library.

# Basic usage
```py
# import the SupercellInbox class
from api import SupercellInbox

# create an instance of SupercellInbox
supercellgame = SupercellInbox(
    "supercellgame", # the subdomain, e.g. supercellgame.inbox.supercell.com
    {"news", "community", "esport"}, # set of available API endpoints, e.g. https://supercellgame.inbox.supercell.com/data/{language}/news/content.json
    {"en", "es", "de", "it", "pl"} # set of available content languages (we only use it in feed generator to fetch content only in available languages for the subdomain)
)

# get the news & events
news = supercellgame.get_news("en")

# get the community content
community = supercellgame.get_community("en")
```