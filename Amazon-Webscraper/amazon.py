import json

from requests import Session, Response


class AccessException(Exception):
    pass


class AmazonSession(Session):
    def __init__(self):
        super().__init__()
        self.headers.update({
            'dnt': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/83.0.4103.61 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
                      'application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': 'https://www.amazon.com/',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8'
        })

        methods = ["get", "post", "put", "delete", "head", "options", "patch"]
        for method in methods:
            setattr(self, method, self.__wrap(method))

    def __exit__(self, *args):
        self.close()

    def home(self) -> Response:
        return self.get('https://www.amazon.in/')

    def search(self, inp: str, page: int = 1) -> Response:
        if page > 1:
            return self.get(f'https://www.amazon.in/s?k={inp}&page={page}')
        return self.get(f'https://www.amazon.in/s?k={inp}')

    def __wrap(self, method):
        def inner(url, **kwargs):
            r = getattr(super(AmazonSession, self), method)(url, **kwargs)
            self.__check_access(r)
            return r

        return inner

    @staticmethod
    def __check_access(response: Response):
        if response.status_code > 500:
            if "To discuss automated access to Amazon data please contact" in response.text:
                raise AccessException("Page was blocked by Amazon. Please try using better proxies")
            else:
                raise AccessException(
                    f"Page must have been blocked by Amazon as the status code was {response.status_code}")


class AmazonSearchResult:
    def __init__(self, title: str, image: str, price: float, original_price: float, discount: int, review: float,
                 review_count: int, link: str, badge: str | None):
        self.__title = title
        self.__image = image
        self.__price = price
        self.__original_price = original_price
        if discount == 0:
            self.__discount = int((1 - (price / original_price)) * 100)
        else:
            self.__discount = discount
        self.__review = review
        self.__review_count = review_count
        self.__link = link
        self.__badge = badge

    def __str__(self):
        from serialize import AmazonSearchResultEncoder
        return json.dumps(self, cls=AmazonSearchResultEncoder)

    def __repr__(self):
        return str(self)

    @property
    def title(self) -> str:
        return self.__title

    @property
    def image(self) -> str:
        return self.__image

    @property
    def price(self) -> float:
        return self.__price

    @property
    def original_price(self) -> float:
        return self.__original_price

    @property
    def discount(self) -> int:
        return self.__discount

    @property
    def review(self) -> float:
        return self.__review

    @property
    def review_count(self) -> int:
        return self.__review_count

    @property
    def link(self) -> str:
        return self.__link

    @property
    def badge(self) -> str | None:
        return self.__badge
