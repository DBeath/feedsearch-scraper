from klein import route, run, Klein, Plating
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from feedsearch_spider import FeedSpider
from lib import get_site_root, coerce_url, create_start_urls, create_allowed_domains
from furl import furl
import json

app = Klein()

class FeedCrawlerRunner(CrawlerRunner):
    def crawl(self, crawler_or_spidercls, *args, **kwargs):
        self.items = []

        crawler = self.create_crawler(crawler_or_spidercls)

        crawler.signals.connect(self.item_scraped, signals.item_scraped)

        print(f"Args: {args}, Kwargs: {kwargs}")
        dfd = self._crawl(crawler, *args, **kwargs)

        dfd.addCallback(self.return_items)
        return dfd

    def item_scraped(self, item, response, spider):
        print(item)
        self.items.append(item)

    def return_items(self, result):
        return self.items


async def return_spider_output(output):
    return json.dumps([dict(item) for item in output], sort_keys=True, indent=2, separators=(',', ': '))

def get_pretty_print(json_object):
    return json.dumps(json_object, sort_keys=True, indent=2, separators=(',', ': '))

@app.route("/")
def hello(request):
    print(request.args)
    #return request.args.get(b'name')
    #return 'Hello World!'
    request.responseHeaders.addRawHeader(b"content-type", b"application/json")
    return request.write(json.dumps({
        "Testing": "Hello World!"
    }).encode('utf-8'))

@app.route("/search")
async def schedule(request):
    print(request)
    print(request.args)
    url = request.args.get(b'url')
    print(type(url))
    if not url:
        return 'No URL'
    url = url[0].decode('utf-8')
    print(f'Getting URL {url}')
    runner = FeedCrawlerRunner()

    url = coerce_url(url)
    print(f'Coerced URL {url}')

    spider = FeedSpider(start_url=url)

    #deferred = runner.crawl(spider, start_urls=start_urls, allowed_domains=[site_root])
    #deferred.addCallback(return_spider_output)

    content = await runner.crawl(spider, start_urls=create_start_urls(url), allowed_domains=create_allowed_domains(url))
    response = await return_spider_output(content)

    request.responseHeaders.addRawHeader(b"content-type", b"application/json")
    # return request.write(deferred)
    return response

app.run("localhost", 8080)
