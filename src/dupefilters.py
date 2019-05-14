from w3lib.url import url_query_cleaner
from scrapy.dupefilters import RFPDupeFilter
from scrapy.utils.request import request_fingerprint
from furl import furl


# https://stackoverflow.com/a/45940517
class NoQueryRFPDupeFilter(RFPDupeFilter):
    def request_fingerprint(self, request):
        query = str(furl(request.url).query)
        if any(map(query.count, ["feedformat=", "feed="])):
            return request_fingerprint(request)
        new_request = request.replace(url=url_query_cleaner(request.url))
        return request_fingerprint(new_request)
