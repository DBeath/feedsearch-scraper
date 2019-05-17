import scrapy


class Feed(scrapy.Item):
    data = scrapy.Field()
    headers = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content_type = scrapy.Field()
    score = scrapy.Field()
    hubs = scrapy.Field()
    version = scrapy.Field()
    description = scrapy.Field()
    bozo = scrapy.Field()
    is_push = scrapy.Field()
    self_url = scrapy.Field()

    def serialize(self):
        return {
            "url": self["url"],
            "title": self["title"],
            "content_type": self["content_type"],
            "version": self["version"]
        }
