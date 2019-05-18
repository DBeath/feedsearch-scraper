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
        serializable = [
            "url",
            "title",
            "content_type",
            "version",
            "score",
            "hubs",
            "description",
            "is_push",
            "self_url",
        ]
        item = {}
        for v in serializable:
            if v in self:
                item[v] = self[v]
        return item

        # return {
        #     "url": self["url"],
        #     "title": self["title"],
        #     "content_type": self["content_type"],
        #     "version": self["version"],
        #     "score": self["score"],
        #     "hubs": self["hubs"],
        #     "description": self["description"],
        #     "is_push": self["is_push"]
        # }
