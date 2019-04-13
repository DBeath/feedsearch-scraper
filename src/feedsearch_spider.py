import scrapy


class FeedSpider(scrapy.Spider):
    name = "links"
    allowed_domains = []
    start_urls = []
    depth_limit = 4

    # def start_requests(self):
    #     urls = [
    #         'https://newyorker.com',
    #     ]
        
    #     for url in urls:
    #         yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
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
            return any(map(url.lower().count, ["rss", "rdf", "xml", "atom", "feed", "json"]))

        for href in response.css('a::attr(href)').extract():
            print(href)
            if is_feedlike_url(href):
                yield response.follow(href, self.parse)

        for href in response.css('link::attr(href)').extract():
            print(href)
            if is_feedlike_url(href):
                yield response.follow(href, self.parse)      
