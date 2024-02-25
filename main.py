#!/usr/bin/python3
# coding:utf-8
from prometheus_client import Gauge, start_http_server, Summary
from prometheus_client.core import CollectorRegistry
import prometheus_client
import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import json
import requests as rq

app = FastAPI()
@app.get('/metrics', response_class=PlainTextResponse)
def get_data():
    es_addr = "http://xxxxx:9200/_cat/shards?format=json&bytes=mb"
    data_str = rq.get(es_addr, auth=('xxxx', 'xxxx'))
    data_arr = json.loads(data_str.content)
    REGISTRY = CollectorRegistry(auto_describe=False)
    opensearch_shards_docs = Gauge("opensearch_shards_docs", "OpenSearch Shards Docs Count", ["index", "shard", "prirep", "ip", "node"], registry=REGISTRY)
    opensearch_shards_size = Gauge("opensearch_shards_size", "OpenSearch Shards Size", ["index", "shard", "prirep", "ip", "node"], registry=REGISTRY)
    for item in data_arr:
        if item['docs'] != None:
            opensearch_shards_docs.labels(item['index'],item['shard'],item['prirep'],item['ip'],item['node']).set(item['docs'])
    for item in data_arr:
        if item['store'] != None:
            opensearch_shards_size.labels(item['index'],item['shard'],item['prirep'],item['ip'],item['node']).set(item['store'])
    return prometheus_client.generate_latest(REGISTRY)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9330, log_level="info")