import scrapy
from lib import query_contains_comments


class FeedSpider(scrapy.Spider):
    name = "links"
    allowed_domains = []
    #start_urls = ['https://newyorker.com']
    depth_limit = 1
    start_urls = []

    def start_requests(self):
        print(f"Start Requests")
        print(vars(self))
        for url in self.start_urls:
            print(f"URL: {url}")
            # yield self.make_requests_from_url(url)
            yield scrapy.Request(url=url, callback=self.parse)

    # def __init__(self, *args, **kwargs):
    #     super(FeedSpider, self).__init__(*args, **kwargs)
    #     print(f"Kwargs: {kwargs}")
    #     self.start_urls = kwargs.get('start_urls')

    def parse(self, response):
        print(f"Followed URL: {response.url}")
        text = response.text
        content_type = response.headers.get('content-type').decode('utf-8')
        data = text.lower()
        # print(content_type)
        if not data:
            return
        if "json" in content_type and data.count("jsonfeed.org"):
            yield {
                'feed_url': response.url
            }
        if bool(data.count("<rss") + data.count("<rdf") + data.count("<feed")):
            yield {
                'feed_url': response.url
            }

        def is_feedlike_url(url):
            url = url.split('?')[0]
            return any(map(url.lower().count, ["rss", "rdf", "xml", "atom", "feed", "json"])) and not query_contains_comments(url)

        for href in response.css('a::attr(href)').extract():
            if is_feedlike_url(href):
                yield response.follow(href, self.parse)

        for href in response.css('link::attr(href)').extract():
            if is_feedlike_url(href):
                yield response.follow(href, self.parse)      
