from amazon import AmazonSearchResult


def filter_price(data: list[AmazonSearchResult], max_price: float) -> list[AmazonSearchResult]:
    return list(filter(lambda x: 0 <= x.price <= max_price, data))


def filter_rating(data: list[AmazonSearchResult], min_rating: float) -> list[AmazonSearchResult]:
    return list(filter(lambda x: x.review >= min_rating, data))


def filter_review_count(data: list[AmazonSearchResult], min_review_count: int) -> list[AmazonSearchResult]:
    return list(filter(lambda x: x.review_count >= min_review_count, data))


def filter_discount(data: list[AmazonSearchResult], min_discount: int) -> list[AmazonSearchResult]:
    return list(filter(lambda x: x.discount >= min_discount, data))
