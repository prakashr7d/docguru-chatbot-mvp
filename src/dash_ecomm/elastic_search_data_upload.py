import click
from dash_ecomm.constants import (
    E_COMM,
    ELASTICSEARCH_URL,
    PRODUCT_EXCEL_SHEET,
    PRODUCTS_JSON,
)
from dash_ecomm.database_utils import get_products_to_json, upload_data_to_elastic
from elasticsearch import Elasticsearch

es = Elasticsearch(ELASTICSEARCH_URL)


@click.group()
def cli():
    pass


@cli.command(name="upload", help="uploads data onto elastic search index")
def upload_data():
    if es.indices.exists(index=E_COMM):
        es.indices.delete(index=E_COMM)
        get_products_to_json(PRODUCT_EXCEL_SHEET)
        upload_data_to_elastic(PRODUCTS_JSON)
    else:
        get_products_to_json(PRODUCT_EXCEL_SHEET)
        upload_data_to_elastic(PRODUCTS_JSON)


@cli.command(name="show", help="shows laptops name from elastic search")
def show_data():
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


if __name__ == "__main__":
    cli()
