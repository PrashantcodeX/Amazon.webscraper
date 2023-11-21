from typing import Literal

from amazon import AmazonSearchResult

SortMethod = Literal["price", "original", "review", "review_count", "discount"]
SortType = Literal["a", "d"]


def sort_data(data: list[AmazonSearchResult], method: SortMethod, sort_type: SortType) -> list[AmazonSearchResult]:
    if method == "price":
        return sorted(data, key=lambda x: x.price, reverse=sort_type == "d")
    elif method == "original":
        return sorted(data, key=lambda x: x.original_price, reverse=sort_type == "d")
    elif method == "review":
        return sorted(data, key=lambda x: x.review, reverse=sort_type == "d")
    elif method == "review_count":
        return sorted(data, key=lambda x: x.review_count, reverse=sort_type == "d")
    elif method == "discount":
        return sorted(data, key=lambda x: x.discount, reverse=sort_type == "d")
    else:
        return data
