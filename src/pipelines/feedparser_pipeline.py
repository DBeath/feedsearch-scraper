from scrapy.exceptions import DropItem
from typing import Tuple, Any, List
import json
import feedparser
import logging

bs4_parser = "lxml"
logger = logging.getLogger(__name__)


class FeedparserPipeline(object):
    def process_item(self, item, spider):
        print(f"Parsing feed {item['url']}")

        # Check link headers first for WebSub content discovery
        # https://www.w3.org/TR/websub/#discovery
        if item["headers"]:
            item["hubs"], item["self_url"] = self.header_links(item["headers"])

        # Try to parse data as JSON
        try:
            json_data = json.loads(item["data"])
            logger.debug("%s data is JSON", self)
            item["content_type"] = "application/json"
            self.parse_json(item, json_data)
            return item
        except json.JSONDecodeError:
            pass

        self.parse_xml(item)
        return item

    def parse_xml(self, item) -> None:
        """
        Get info from XML (RSS or ATOM) feed.
        :param data: XML string
        :return: None
        """

        # Parse data with feedparser
        # Don't wrap this in try/except, feedparser eats errors and returns bozo instead
        parsed = self.parse_feed(item["data"])
        if not parsed or parsed.get("bozo") == 1:
            item["bozo"] = 1
            logger.warning("No valid feed data in %s", self.url)
            return

        feed = parsed.get("feed")

        # Only search if no hubs already present from headers
        if not item["hubs"]:
            item["hubs"], item["self_url"] = self.websub_links(feed)

        if item["hubs"] and item["self_url"]:
            item["is_push"] = True

        item["version"] = parsed.get("version")
        item["title"] = self.feed_title(feed)
        item["description"] = self.feed_description(feed)

    def parse_json(self, item, data: dict) -> None:
        """
        Get info from JSON feed.

        :param data: JSON object
        :return: None
        """
        item["version"] = data.get("version")
        if "https://jsonfeed.org/version/" not in item["version"]:
            item["bozo"] = 1
            return

        feed_url = data.get("feed_url")

        item["title"] = data.get("title")
        item["description"] = data.get("description")

        favicon = data.get("favicon")
        if favicon:
            item["favicon"] = favicon

        # Only search if no hubs already present from headers
        if not item["hubs"]:
            try:
                item["hubs"] = list(hub.get("url") for hub in data.get("hubs", []))
            except (IndexError, AttributeError):
                pass

        if item["hubs"]:
            item["is_push"] = True

    @staticmethod
    def parse_feed(text: str) -> dict:
        """
        Parse feed with feedparser.

        :param text: Feed string
        :return: dict
        """
        return feedparser.parse(text)

    @staticmethod
    def feed_title(feed: dict) -> str:
        """
        Get feed title

        :param feed: feed dict
        :return: str
        """
        title = feed.get("title", None)
        if not title:
            return ""
        return FeedparserPipeline.clean_title(title)

    @staticmethod
    def clean_title(title: str) -> str:
        """
        Cleans title string, and shortens if too long.
        Have had issues with dodgy feed titles.

        :param title: Title string
        :return: str
        """
        try:
            title = BeautifulSoup(title, bs4_parser).get_text()
            if len(title) > 1024:
                title = title[:1020] + "..."
            return title
        except Exception as ex:
            logger.exception("Failed to clean title: %s", ex)
            return ""

    @staticmethod
    def feed_description(feed: dict) -> str:
        """
        Get feed description.

        :param feed: feed dict
        :return: str
        """
        subtitle = feed.get("subtitle", None)
        if subtitle:
            return subtitle
        return feed.get("description", None)

    @staticmethod
    def websub_links(feed: dict) -> Tuple[List[str], str]:
        """
        Returns a tuple containing the hub url and the self url for
        a parsed feed.

        :param parsed: An RSS feed parsed by feedparser
        :type parsed: dict
        :return: tuple
        """
        links = feed.get("links", [])
        return FeedparserPipeline.find_hubs_and_self_links(links)

    @staticmethod
    def header_links(headers: dict) -> Tuple[List[str], str]:
        """
        Attempt to get self and hub links from HTTP headers
        https://www.w3.org/TR/websub/#x4-discovery

        :param headers: Dict of HTTP headers
        :return: None
        """
        link_header = headers.get("Link")
        links: list = []
        if link_header:
            links = parse_header_links(link_header)
        return FeedparserPipeline.find_hubs_and_self_links(links)

    @staticmethod
    def find_hubs_and_self_links(links: List[dict]) -> Tuple[List[str], str]:
        """
        Parses a list of links into self and hubs urls

        :param links: List of parsed HTTP Link Dicts
        :return: Tuple
        """
        hub_urls: List[str] = []
        self_url: str = ""

        if not links:
            return [], ""

        for link in links:
            try:
                if link["rel"] == "hub":
                    href: str = link["href"]
                    hub_urls.append(href)
                elif link["rel"] == "self":
                    self_url = link["href"]
            except KeyError:
                continue

        return hub_urls, self_url
