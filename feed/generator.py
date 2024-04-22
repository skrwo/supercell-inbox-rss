from feedgen.feed import FeedGenerator
from api import SupercellInbox
from helpers.case_util import split_camel_case
from datetime import datetime, UTC
from pathlib import Path
from urllib.parse import urlparse
from mimetypes import guess_type


def key_to_url_path(key: str):
    m = {"newsEntries": "news"}
    return m.get(key)


def key_to_file_name(key: str):
    m = {"eventEntries": "events"}
    return m.get(key)


def get_button_url(link_data: dict, language: str, inbox: SupercellInbox) -> str | None:
    url_type = link_data["urlType"]
    url = link_data["url"]
    id = link_data.get("id")
    if not id:
        print("no id in button data", inbox.subdomain, language)
        print(link_data)

    if url_type == "url":
        url = url \
            .replace("brawlstars-inbox://", "brawlstars://") \
            .replace("hayday-inbox://", "hayday://")
    elif url_type == "article":
        article_id = link_data["url"]["id"]
        section_key = link_data["url"]["section"]

        if path := key_to_url_path(section_key):
            url = inbox.compose_resource_url(f"#/{language}/{path}/{article_id}")
        else:
            print(f"[!] Unknown URL section: {url_type} [{inbox.subdomain}/{id}]")
            return

    return url


def get_button_html(
    link_data: dict, language: str, inbox: SupercellInbox
) -> str | None:
    url = link_data["url"]
    label = link_data["label"]

    url = get_button_url(link_data, language, inbox)

    return f'<a href="{url}">👉{label}👈</a>'


def save_feed(feed: FeedGenerator, directory: str, language: str, filename: str):
    path = f"./rss/{directory}"
    Path(path).mkdir(exist_ok=True)

    path += f"/{language}"
    Path(path).mkdir(exist_ok=True)

    feed.rss_file(
        f"{path}/{filename}.xml",
        pretty=True,
    )
    feed.atom_file(
        f"{path}/{filename}.atom",
        pretty=True,
    )


def generate_feed(
    inbox: SupercellInbox, language: str, key: str, data: dict
) -> FeedGenerator:
    feed = FeedGenerator()
    feed.id(f"{inbox.subdomain}-{key}-{language}")
    feed.language(language)
    feed.link(href="https://github.com/skrwo/supercell-inbox-rss/")

    # remove the "entries" word, titlecase
    title = " ".join(map(lambda x: x.title(), split_camel_case(key)[:-1]))

    feed.title(f"{inbox.subdomain.title()} - {title}")
    feed.description(f"RSS wrapper of {inbox.subdomain.title()} inbox {title}")

    entries: list[dict] = data["entries"][key]

    for entry in entries:
        entry_id = entry["id"]

        e = feed.add_entry()
        e.id(entry_id)

        e.title(entry["title"] if not entry.get("hideTitle") else "🗞️")
        e.published(datetime.fromtimestamp(float(entry["postDate"]), UTC))

        if (metadata := entry.get("metadata")) and (
            published_at := metadata.get("publishedAt")
        ):
            e.updated(published_at)

        if path := key_to_url_path(key):
            e.link(
                href=inbox.compose_resource_url(f"#/{language}/{path}/{entry_id}"),
                rel="alternate",
                hreflang=language,
            )

        if creator := entry.get("creator"):
            author = tuple(creator.values())[0]
            e.author(name=author["name"])

        if categories := entry.get("categories"):
            for c in categories:
                e.category(term=c["title"])

        if thumbnail := (entry.get("thumbnail") or entry.get("background")):
            thumbnail_path = tuple(thumbnail.values())[-1]["path"]
            thumbnail_url = inbox.compose_resource_url(thumbnail_path)

            filepath: str = urlparse(thumbnail_path).path

            # yt video thumbnail names are similar to .jpg-<timestamp>, so we strip the timestamp part
            if filepath[-1].isdigit():
                filepath = filepath[0 : filepath.rfind("-")]

            mimetype, _ = guess_type(filepath)
            if not mimetype:
                print("no mimetype:", thumbnail_url)
                print("path:", filepath)

                # mimetype must be provided so let's pretend it's jpeg
                mimetype = "image/jpeg+unknown"

            # must we actually do this? (looks like it works with 0)
            length = 0  # or inbox.get_resource_length(thumbnail_url)

            e.enclosure(thumbnail_url, type=mimetype, length=length)

        if embed := entry.get("embed"):
            e.link(href=embed["url"], rel="alternate")
        elif url := (entry.get("url") or entry.get("videoUrl")):
            e.link(href=url, rel="alternate")

        if (details := entry.get("details")) or (ctas := entry.get("ctas")):
            contents_html = []
            if details:
                for detail in details.values():
                    if title := detail.get("title"):
                        contents_html.append(f"<h1>{title}</h1>")
                    if (detail_type := detail.get("type")) in {
                        "textBlock",
                        "featureBlock",
                    }:
                        if image := detail.get("image"):
                            image = tuple(image.values())[-1]
                            image_url = inbox.compose_resource_url(image["path"])
                            contents_html.append(f'<img src="{image_url}">')
                        contents_html.append(detail["body"])
                    elif detail_type == "pollBlock":
                        contents_html.append("📊 [POLL]")
                        contents_html.append("<ul>")
                        for option in detail["poll"]["options"]:
                            title_html = ""
                            if title := option.get("title"):
                                title_html = f"<p>{title}</p>"
                            image = tuple(option["image"].values())[-1]
                            image_url = inbox.compose_resource_url(image["path"])
                            contents_html.append(
                                f'<li>{title_html}<img src="{image_url}"></li>'
                            )
                        contents_html.append("</ul>")
                    elif detail_type == "buttonBlock":
                        if html := get_button_html(detail, language, inbox):
                            contents_html.append(html)
                    elif detail_type == "imageBlock":
                        image = tuple(detail["image"].values())[-1]
                        image_url = inbox.compose_resource_url(image["path"])
                        contents_html.append(f'<img src="{image_url}">')
                    elif detail_type == "videoBlock":
                        embed = detail["embed"]
                        url = embed["url"]
                        contents_html.append(f'<a href="{url}">📺 [EMBEDDED VIDEO]</a>')
                    else:
                        print(
                            f"[!] Unknown detail type skipped: '{detail_type}' in '{inbox.subdomain}' domain [{key}/{entry_id}]"
                        )

            # Call-To-Actions buttons (typecally eventsEntries)
            if ctas := entry.get("ctas"):
                contents_html.append("<br>")
                ctas_html = []
                for cta in ctas.values():
                    if html := get_button_html(cta, language, inbox):
                        ctas_html.append(html)
                contents_html.append(" -- ".join(ctas_html))

                if len(ctas) == 1:
                    e.link(
                        href=get_button_url(tuple(ctas.values())[0], language, inbox),
                        rel="alternate",
                    )

            if contents_html:
                e.content("\n".join(contents_html))

        elif entry.get("displayTimer"):
            label = entry["timerLabel"]
            target_date_timestamp = float(entry["timerTarget"])
            target_date = datetime.fromtimestamp(target_date_timestamp, UTC)
            date_str = target_date.strftime("%H:%M, %d.%m.%Y")
            now = datetime.now(UTC)
            if now > target_date:
                e.content(f"⏱️ [TIMER] set to {date_str} (UTC) - Expired!")
            else:
                difference_date = now - target_date
                difference_seconds = difference_date.total_seconds()
                if difference_seconds >= 24 * 60 * 60:
                    last_str = f" {difference_date.days} days, " + target_date.strftime(
                        "%H hours, %M minutes"
                    )
                elif difference_seconds >= 60 * 60:
                    last_str = target_date.strftime("%H hours, %M minutes")
                elif difference_seconds >= 60:
                    last_str = target_date.strftime("%M minutes, %S seconds")
                else:
                    last_str = target_date.strftime("%S seconds")
                e.content(f"⏱️ [TIMER] set to {date_str} (UTC) - {label} {last_str}")
        elif "ctas" in entry:
            # if event entry has CTAs key but its empty inside
            # (content is required for ATOM feeds)
            e.content("[EMPTY]")
        else:
            # Looks like it works without "[EMPTY]" at the moment
            ...
            # ATOM requires content or link so we must add something as content
            # e.content("[EMPTY]")

        if not e.content() and not e.link():
            print("empty entry:", inbox.subdomain, key, entry_id)
            print("keys:", entry.keys())
            e.content("[EMPTY]")

    return feed


def generate_feeds(inbox: SupercellInbox, language: str):
    for endpoint, data in {
        "news": inbox.get_news(language),
        "community": inbox.get_community(language),
        "esport": inbox.get_esport(language),
    }.items():
        if not data:
            # 'news' are always available, if language is supported
            if endpoint == "news":
                return
            continue

        for key in {
            "eventEntries",
            "newsEntries",
            "communityEntries",
            "esportNewsEntries",
        }:
            if key in data.get("entries", {}):

                feed = generate_feed(inbox, language, key, data)
                filename = key_to_file_name(key) or endpoint
                try:
                    save_feed(feed, inbox.subdomain, language, filename)
                except ValueError as e:
                    print("[!] failed to save", inbox.subdomain, language, key)
                    print("error:", e)
                    # raise
                continue
