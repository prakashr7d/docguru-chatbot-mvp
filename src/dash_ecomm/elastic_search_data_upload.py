from dash_ecomm.database_utils import get_products_to_json, upload_data_to_elastic
from elasticsearch import Elasticsearch

get_products_to_json("e-comm-products.xlsx")
upload_data_to_elastic("products.json")
es = Elasticsearch("http://localhost:9200")
query = {
    "_source": [],
    "size": 5,
    "query": {
        "bool": {
            "filter": [
                {"multi_match": {"query": "laptops", "fields": ["sub_category"]}}
            ]
        }
    },
}

products = es.search(index="e_comm", body=query, scroll="1m")
for i in products["hits"]["hits"]:
    print(i["_source"]["brand"])
# products = es.search(index="e_comm", body=query)
# for i in products:
#     print(i)
