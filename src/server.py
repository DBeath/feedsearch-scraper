from klein import route, run
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from feedsearch_spider import FeedSpider
from lib import get_site_root, coerce_url
import json


class FeedCrawlerRunner(CrawlerRunner):
    def crawl(self, crawler_or_spidercls, *args, **kwargs):
        self.items = []

        crawler = self.create_crawler(crawler_or_spidercls)

        crawler.signals.connect(self.item_scraped, signals.item_scraped)

        dfd = self._crawl(crawler, *args, **kwargs)

        dfd.addCallback(self.return_items)
        return dfd

    def item_scraped(self, item, response, spider):
        self.items.append(item)

    def return_items(self, result):
        return self.items


def return_spider_output(output):
    return json.dumps([dict(item) for item in output])

@route("/")
def hello(request):
    print(request.args)
    return request.args.get(b'name')
    return 'Hello World!'

@route("/search")
def schedule(request):
    print(request)
    print(request.args)
    url = request.args.get(b'url')
    print(f'Getting URL {url}')
    runner = FeedCrawlerRunner()
    spider = FeedSpider()
    spider.allowed_domains = get_site_root(url)
    url = coerce_url(url)
    print(f'Coerced URL {url}')

    spider.start_urls = url
    deferred = runner.crawl(spider)
    deferred.addCallback(return_spider_output)
    return deferred

run("localhost", 8080)
