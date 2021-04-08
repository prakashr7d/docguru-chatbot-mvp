from elasticsearch import Elasticsearch

# upload_data_to_elastic("products.json")
es = Elasticsearch("http://localhost:9200")
query = {
    "_source": [],
    "query": {
        "bool": {
            "filter": [{"multi_match": {"query": "laptops", "fields": ["category"]}}]
        }
    },
}

products = es.search(index="e_comm", body=query)
print(products)
for i in products["hits"]["hits"]:
    print(i["_source"]["brand"])
# products = es.search(index="e_comm", body=query)
# for i in products:
#     print(i)
