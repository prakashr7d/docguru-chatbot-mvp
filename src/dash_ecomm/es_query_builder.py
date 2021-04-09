import logging
from typing import Dict, Text

from dash_ecomm.constants import _SOURCE, BRAND, CATEGORY, PRICE, SUB_CATEGORY
from elasticsearch import Elasticsearch

logger = logging.getLogger("query_builder")


class EsQueryBuilder:
    def __init__(self):
        self.es = Elasticsearch("http://es01:9200")

    def product_search_with_category(self, message: Text):
        product_search = {
            "_source": [],
            "query": {
                "bool": {
                    "filter": [
                        {
                            "multi_match": {
                                "query": f"{message}",
                                "fields": ["sub_category"],
                            }
                        }
                    ]
                }
            },
        }
        products = self.es.search(index="e_comm", body=product_search)
        logger.debug(type(products))
        # count = self.es.count(index="e_comm", body=product_search)
        return products

    def product_search_with_price(
        self, message: Text, price_min: int, price_max: int
    ) -> (Dict, int):
        product_search = {
            _SOURCE: [],
            "query": {
                "bool": {
                    "filter": [
                        {
                            "multi_match": {
                                "query": message,
                                "fields": [CATEGORY, SUB_CATEGORY],
                                "operator": "or",
                            }
                        },
                        {"range": {PRICE: {"gte": price_min, "lte": price_max}}},
                    ]
                }
            },
        }
        products = self.es.search(index="e_comm", body=product_search)
        count = self.es.count(index="e_comm", body=product_search)
        return products, count

    def product_search_with_colors_price(self) -> Dict:
        pass

    def product_search_with_brand(self, message: Text) -> (Dict, int):
        product_search = {
            _SOURCE: [],
            "query": {
                "bool": {
                    "filter": [
                        {
                            "multi_match": {
                                "query": f"{message}",
                                "fields": [CATEGORY, SUB_CATEGORY, BRAND + "^3"],
                                "operator": "and",
                            }
                        }
                    ]
                }
            },
        }
        products = self.es.search(index="e_comm", body=product_search)
        count = self.es.count(index="e_comm", body=product_search)
        return products, count

    def product_search_with_gender(self) -> Dict:
        pass

    def product_search_with_all(self) -> Dict:
        pass
