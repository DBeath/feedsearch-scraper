from werkzeug.urls import url_parse, url_fix

def coerce_url(url: str, https: bool=True) -> str:
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
    parsed = url_parse(url, scheme="http")
    return parsed.netloc
