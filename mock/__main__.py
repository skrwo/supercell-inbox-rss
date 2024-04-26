from pathlib import Path
from api import INBOXES
from json import dumps

lang = "en"

for inbox in INBOXES:
    directory = f"./mock/{inbox.subdomain}"
    Path(directory).mkdir(exist_ok=True)

    if news := inbox.get_news(lang):
        Path(f"{directory}/news.json").write_text(dumps(news, indent=4))
    
    if community := inbox.get_community(lang):
        Path(f"{directory}/community.json").write_text(dumps(community, indent=4))
    
    if esport := inbox.get_esport(lang):
        Path(f"{directory}/esport.json").write_text(dumps(esport, indent=4))
