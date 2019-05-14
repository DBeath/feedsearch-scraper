import scrapy

class Feed(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    content_type = scrapy.Field()
    score = scrapy.Field()