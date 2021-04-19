import logging
from typing import Dict, Text

from elasticsearch import Elasticsearch

logger = logging.getLogger(__name__)


class EsQueryBuilder:
    def __init__(self):
        self.es = Elasticsearch("http://elasticsearch:9200")

    def product_search_with_scroll(self, scroll_id):
        products = self.es.scroll(scroll_id=scroll_id, scroll="1m")
        return products

    def product_search_with_category(self, category: Text):
        product_search = {
            "_source": [],
            "size": 5,
            "query": {
                "bool": {
                    "filter": [
                        {
                            "multi_match": {
                                "query": f"{category}",
                                "type": "best_fields",
                                "fields": ["category", "sub_category"],
                                "operator": "and",
                            }
                        }
                    ]
                }
            },
        }
        products = self.es.search(index="e_comm", body=product_search, scroll="1m")
        logger.info(f"scroll: {products}")
        return products

    def product_search_with_price(
        self, message: Text, price_min: int, price_max: int
    ) -> (Dict, int):
        product_search = {
            "_source": [],
            "size": 5,
            "query": {
                "bool": {
                    "filter": [
                        {
                            "multi_match": {
                                "query": message,
                                "type": "best_fields",
                                "fields": ["category", "sub_category"],
                                "operator": "or",
                            }
                        },
                        {"range": {"price": {"gte": price_min, "lte": price_max}}},
                    ]
                }
            },
        }
        products = self.es.search(index="e_comm", body=product_search, scroll="1m")
        # count = self.es.count(index="e_comm", body=product_search)
        return products

    def product_search_with_price_max(
        self, message: Text, price_max: int
    ) -> (Dict, int):
        product_search = {
            "_source": [],
            "size": 5,
            "query": {
                "bool": {
                    "filter": [
                        {
                            "multi_match": {
                                "query": f"{message}",
                                "fields": ["category", "sub_category"],
                                "operator": "or",
                            }
                        },
                        {"range": {"price": {"lte": price_max}}},
                    ]
                }
            },
        }
        products = self.es.search(index="e_comm", body=product_search, scroll="1m")
        # count = self.es.count(index="e_comm", body=product_search)
        return products

    def product_search_with_price_min(
        self, message: Text, price_min: int
    ) -> (Dict, int):
        product_search = {
            "_source": [],
            "size": 5,
            "query": {
                "bool": {
                    "filter": [
                        {
                            "multi_match": {
                                "query": message,
                                "type": "best_fields",
                                "fields": ["category", "sub_category"],
                                "operator": "or",
                            }
                        },
                        {"range": {"price": {"gte": price_min}}},
                    ]
                }
            },
        }
        products = self.es.search(index="e_comm", body=product_search, scroll="1m")
        return products

    def product_search_with_colors(self, message: Text) -> Dict:
        product_search = {
            "_source": [],
            "size": 5,
            "query": {
                "bool": {
                    "filter": [
                        {
                            "multi_match": {
                                "query": f"{message}",
                                "fields": ["sub_category", "color"],
                                "operator": "and",
                            }
                        }
                    ]
                }
            },
        }
        products = self.es.search(index="e_comm", body=product_search, scroll="1m")
        return products

    def product_search_with_brand(self, brand: Text) -> (Dict, int):
        product_search = {
            "_source": [],
            "size": 5,
            "query": {
                "bool": {
                    "filter": [
                        {
                            "multi_match": {
                                "query": f"{brand}",
                                "fields": ["brand"],
                                "operator": "or",
                            }
                        }
                    ]
                }
            },
        }
        products = self.es.search(index="e_comm", body=product_search, scroll="1m")
        return products

    def product_search_with_gender(self, message: Text) -> Dict:
        product_search = {
            "_source": [],
            "size": 5,
            "query": {
                "bool": {
                    "filter": [
                        {
                            "multi_match": {
                                "query": f"{message}",
                                "fields": ["sub_category", "gender"],
                                "operator": "or",
                            }
                        }
                    ]
                }
            },
        }
        products = self.es.search(index="e_comm", body=product_search, scroll="1m")
        return products

    def product_search_with_all(
        self, message: Text, price_min: int, price_max: int
    ) -> Dict:
        product_search = {
            "_source": [],
            "size": 5,
            "query": {
                "bool": {
                    "filter": [
                        {
                            "multi_match": {
                                "query": message,
                                "fields": [
                                    "category",
                                    "sub_category",
                                    "brand",
                                    "gender",
                                    "color",
                                ],
                                "operator": "and",
                            }
                        },
                        {"range": {"price": {"gte": price_min, "lte": price_max}}},
                    ]
                }
            },
        }
        products = self.es.search(index="e_comm", body=product_search, scroll="1m")
        return products
