import json
import os
from klein import route, run, Klein, Plating
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from feedsearch_spider import FeedSpider
from lib import get_site_root, coerce_url, create_start_urls, create_allowed_domains
from jinja2 import Template, Environment, FileSystemLoader
from furl import furl


thisdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

j2_env = Environment(loader=FileSystemLoader(thisdir), trim_blocks=True)

# https://stackoverflow.com/questions/36384286/how-to-integrate-flask-scrapy

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
    return json.dumps(
        [dict(item) for item in output],
        sort_keys=True,
        indent=2,
        separators=(",", ": "),
    )


def get_pretty_print(json_object):
    return json.dumps(json_object, sort_keys=True, indent=2, separators=(",", ": "))


def str_to_bool(value):
    if not value or not isinstance(value, str):
        return False
    print(f"Value {value}")
    return value.lower() in ("true", "t", "yes", "y", "1")


def request_arg_str(request, arg_name):
    value = request.args.get(arg_name.encode("utf-8"))
    if not value:
        return None
    return value[0].decode("utf-8")


@app.route("/")
def hello(request):
    template = j2_env.get_template("index.html")
    html = template.render(message="Hello World!")
    return request.write(html.encode("utf-8"))
    # request.responseHeaders.addRawHeader(b"content-type", b"application/json")
    # return request.write(json.dumps({
    #     "Testing": "Hello World!"
    # }).encode('utf-8'))


@app.route("/search")
async def schedule(request):
    url = request_arg_str(request, "url")
    render_result = str_to_bool(request_arg_str(request, "result"))

    if not url:
        return "No URL"

    print(f"Getting URL: {url}")
    print(f"Render Result: {render_result}")

    url = coerce_url(url)
    print(f"Coerced URL: {url}")

    runner = FeedCrawlerRunner()
    spider = FeedSpider(start_url=url)

    # deferred = runner.crawl(spider, start_urls=start_urls, allowed_domains=[site_root])
    # deferred.addCallback(return_spider_output)

    content = await runner.crawl(
        spider,
        start_urls=create_start_urls(url),
        allowed_domains=create_allowed_domains(url),
    )

    if render_result:
        print("Render result as html")
        template = j2_env.get_template("results.html")
        html = template.render(feeds=content, url=url)
        return request.write(html.encode("utf-8"))

    response = await return_spider_output(content)
    request.responseHeaders.addRawHeader(b"content-type", b"application/json")
    # return request.write(deferred)
    return response


app.run("localhost", 8080)
