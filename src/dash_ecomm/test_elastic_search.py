from dash_ecomm.database_utils import upload_data_to_elastic
from elasticsearch import Elasticsearch

upload_data_to_elastic("products.json")
es = Elasticsearch([{"host": "localhost", "port": 9200}])
print(
    es.search(
        index="e_comm", body={"size": 1, "query": {"bool": {"category": "laptops"}}}
    )
)
