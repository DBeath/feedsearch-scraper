from w3lib.url import url_query_cleaner
from scrapy.dupefilters import RFPDupeFilter
from scrapy.utils.request import request_fingerprint

# https://stackoverflow.com/a/45940517
class NoQueryRFPDupeFilter(RFPDupeFilter):

    def request_fingerprint(self, request):
        new_request = request.replace(url=url_query_cleaner(request.url))
        return request_fingerprint(new_request)