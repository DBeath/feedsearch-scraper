from scrapy.exceptions import DropItem


class DuplicatesPipeline(object):
    def __init__(self):
        self.urls_seen = set()

    def process_item(self, item, spider):
        url = item["url"].strip("/")
        if url in self.urls_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.urls_seen.add(url)
            return item
