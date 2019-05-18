from werkzeug.urls import url_parse, url_fix
from furl import furl
from typing import List


def coerce_url(url: str, https: bool = False) -> str:
    """
    Coerce URL to valid format

    :param url: URL
    :param https: Force https if no scheme in url
    :return: str
    """
    url.strip()
    if url.startswith("feed://"):
        return url_fix(f"http://{url[7:]}")
    for proto in ["http://", "https://"]:
        if url.startswith(proto):
            return url_fix(url)
    if https:
        return url_fix(f"https://{url}")
    else:
        return url_fix(f"http://{url}")


def get_site_root(url: str) -> str:
    """
    Find the root domain of a url
    """
    url = coerce_url(url)
    parsed = furl(url)
    return parsed.host


def create_start_urls(url: str) -> List[str]:
    origin = furl(url).origin
    f_origin = furl(origin)

    start_urls = [url, origin]
    start_urls.append(str(f_origin.add(path="/about")))
    return start_urls


def create_allowed_domains(url: str) -> List[str]:
    parsed = furl(url)
    return [parsed.host]


def query_contains_comments(url: str) -> bool:
    query = str(furl(url).query)
    return any(map(query.count, ["comment=", "comments=", "post="]))


def is_feedlike_url(url):
    return any(map(url.lower().count, ["rss", "rdf", "xml", "atom", "feed", "json"]))


def parse_header_links(value):
    """
    Return a list of Dicts of parsed link headers proxies.
    i.e. Link: <http:/.../front.jpeg>; rel=front; type="image/jpeg",
    <http://.../back.jpeg>; rel=back;type="image/jpeg"

    :param value: HTTP Link header to parse
    :return: List of Dicts
    """

    links = []

    replace_chars = " '\""

    for val in value.split(","):
        try:
            url, params = val.split(";", 1)
        except ValueError:
            url, params = val, ""

        link = {}

        link["url"] = url.strip("<> '\"")

        for param in params.split(";"):
            try:
                key, value = param.split("=")
            except ValueError:
                break

            link[key.strip(replace_chars)] = value.strip(replace_chars)

        links.append(link)

    return links
