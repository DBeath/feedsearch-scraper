import scrapy
from lib import query_contains_comments
from dupefilters import NoQueryRFPDupeFilter
from feed import Feed
import logging
from scrapy.utils.log import configure_logging


class FeedSpider(scrapy.Spider):
    name = "links"
    allowed_domains = []
    depth_limit = 2
    start_urls = []

    custom_settings = {
        "DUPEFILTER_CLASS": "dupefilters.NoQueryRFPDupeFilter",
        "ITEM_PIPELINES": {
            "pipelines.duplicates_pipeline.DuplicatesPipeline": 300,
            "pipelines.feedparser_pipeline.FeedparserPipeline": 400
        },
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36",
    }

    # configure_logging(install_root_handler=False)
    # logging.basicConfig(
    #     format='%(levelname)s: %(message)s',
    #     level=logging.INFO
    # )

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
        headers = response.headers
        content_type = ""
        try:
            content_type = response.headers.get("content-type").decode("utf-8")
        except:
            pass
        data = text.lower()

        if not data:
            return

        if "json" in content_type and data.count("jsonfeed.org"):
            yield Feed(url=response.url, content_type=content_type, data=text, headers=headers)

        if bool(data.count("<rss") + data.count("<rdf") + data.count("<feed")):
            yield Feed(url=response.url, content_type=content_type, data=text, headers=headers)

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
