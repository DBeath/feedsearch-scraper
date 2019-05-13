import scrapy
from lib import query_contains_comments
from dupefilters import NoQueryRFPDupeFilter
from feed import Feed
import feedparser


class FeedSpider(scrapy.Spider):
    name = "links"
    allowed_domains = []
    depth_limit = 2
    start_urls = []

    custom_settings = {
        "DUPEFILTER_CLASS": "dupefilters.NoQueryRFPDupeFilter",
        "ITEM_PIPELINES": {"pipelines.duplicates_pipeline.DuplicatesPipeline": 300},
    }

    def start_requests(self):
        print(f"Start Requests")
        print(vars(self))
        print(self.settings)
        for url in self.start_urls:
            print(f"URL: {url}")
            yield scrapy.Request(url=url, callback=self.parse)

    # def __init__(self, *args, **kwargs):
    #     super(FeedSpider, self).__init__(*args, **kwargs)
    #     print(f"Kwargs: {kwargs}")
    #     self.start_urls = kwargs.get('start_urls')

    def parse(self, response):
        print(f"Followed URL: {response.url}")
        text = response.text
        content_type = response.headers.get("content-type").decode("utf-8")
        data = text.lower()

        if not data:
            return

        if "json" in content_type and data.count("jsonfeed.org"):
            yield Feed(url=response.url, content_type=content_type)

        if bool(data.count("<rss") + data.count("<rdf") + data.count("<feed")):
            parsed = feedparser.parse(text)
            feed = parsed.get("feed")
            title = feed.get("title")
            yield Feed(url=response.url, content_type=content_type, title=title)

        def is_feedlike_url(url):
            return any(
                map(url.lower().count, ["rss", "rdf", "xml", "atom", "feed", "json"])
            )

        def should_follow_url(url: str) -> bool:
            if "/amp/" in url:
                return False
            if query_contains_comments(url):
                return False
            if is_feedlike_url(url):
                return True
            return False

        links = []
        links.extend(response.css("a::attr(href)").getall())
        links.extend(response.css("link::attr(href)").getall())

        # print(links)
        for href in links:
            # print(href)
            if should_follow_url(href):
                # print(f"Folling URL: {href}")
                yield response.follow(href, self.parse)
            else:
                print(f"Not following URL: {href}")
