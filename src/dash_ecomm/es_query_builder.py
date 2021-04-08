import logging
from typing import Dict, Text

from elasticsearch import Elasticsearch

logger = logging.getLogger("query_builder")


class EsQueryBuilder:
    def __init__(self):
        self.es = Elasticsearch("http://es03:9200")

    def product_search_with_category(self, message: Text):
        product_search = {
            "_source": [],
            "query": {
                "bool": {
                    "filter": [
                        {"multi_match": {"query": f"{message}", "fields": ["category"]}}
                    ]
                }
            },
        }
        products = self.es.search(index="e_comm", body=product_search)
        return products

    def product_search_with_price(
        self, message: Text, price_min: int, price_max: int
    ) -> Dict:
        product_search = {
            "_source": [],
            "query": {
                "bool": {
                    "filter": [
                        {"multi_match": {"query": message, "fields": ["category"]}},
                        {"range": {"price": {"gte": price_min, "lte": price_max}}},
                    ]
                }
            },
        }
        products = self.es.search(index="e_comm", body=product_search)
        return products

    def product_search_with_colors_price(self) -> Dict:
        pass

    def product_search_with_brand(self, message: Text) -> Dict:
        product_search = {
            "_source": [],
            "query": {
                "bool": {
                    "filter": [
                        {
                            "multi_match": {
                                "query": f"{message}",
                                "fields": ["category", "brand"],
                                "operator": "and",
                            }
                        }
                    ]
                }
            },
        }
        products = self.es.search(index="e_comm", body=product_search)
        return products

    def product_search_with_gender(self) -> Dict:
        pass

    def product_search_with_all(self) -> Dict:
        pass
