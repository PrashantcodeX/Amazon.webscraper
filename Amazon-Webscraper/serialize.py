from json import JSONEncoder, JSONDecoder

from amazon import AmazonSearchResult
from numbercast import parse_float, parse_int


class AmazonSearchResultEncoder(JSONEncoder, JSONDecoder):

    def __init__(self, **kwargs):
        kwargs['indent'] = 4
        JSONEncoder.__init__(self, **kwargs)
        JSONDecoder.__init__(self, object_hook=self.from_dict)

    def default(self, o: AmazonSearchResult):
        return {
            'title': o.title,
            'image': o.image,
            'price': o.price,
            'original_price': o.original_price,
            'discount': o.discount,
            'review': o.review,
            'review_count': o.review_count,
            'link': o.link,
            'badge': o.badge
        }

    @staticmethod
    def from_dict(d: dict[str, str | None]) -> AmazonSearchResult:
        try:
            return AmazonSearchResult(
                d['title'],
                d['image'],
                parse_float(d['price'].replace(',', '')) if d['price'] else -1,
                parse_float(d['original_price'].replace('\u20b9', '').replace(',', '')) if d['original_price'] else -1,
                parse_int((d['discount'][1:4]).replace('%', '')) if d['discount'] else 0,
                parse_float(d['review'].replace(' out of 5 stars', '')) if d['review'] else 0,
                parse_int(d['review_count'].replace(',', '')) if d['review_count'] else 0,
                'https://www.amazon.in' + d['link'],
                d['badge']
            )
        except Exception as e:
            print(d)
            raise e
