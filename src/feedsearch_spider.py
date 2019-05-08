import scrapy
from lib import query_contains_comments
from dupefilters import NoQueryRFPDupeFilter


class FeedSpider(scrapy.Spider):
    name = "links"
    allowed_domains = []
    #start_urls = ['https://newyorker.com']
    depth_limit = 2
    start_urls = []

    custom_settings = {
        'DUPEFILTER_CLASS' : 'dupefilters.NoQueryRFPDupeFilter',
    }

    def start_requests(self):
        print(f"Start Requests")
        print(vars(self))
        print(self.settings)
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
            # if query_contains_comments(url):
            #     return False
            return any(map(url.lower().count, ["rss", "rdf", "xml", "atom", "feed", "json"]))

        def should_follow_url(url: str) -> bool:
            if '/amp/' in url:
                return False
            if query_contains_comments(url):
                return False
            if is_feedlike_url(url):
                return True
            return False

        links = []
        links.extend(response.css('a::attr(href)').getall())
        links.extend(response.css('link::attr(href)').getall())

        #print(links)
        for href in links:
            # print(href)
            if should_follow_url(href):
                #print(f"Folling URL: {href}")
                yield response.follow(href, self.parse)
            else:
                print(f"Not following URL: {href}")
            # yield response.follow(href, self.parse)

        # for href in response.css('a::attr(href)').extract():
        #     if is_feedlike_url(href):
        #         yield response.follow(href, self.parse)

        # for href in response.css('link::attr(href)').extract():
        #     if is_feedlike_url(href):
        #         yield response.follow(href, self.parse)
