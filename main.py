#!/usr/bin/python3
# coding:utf-8
from prometheus_client import Gauge, start_http_server, Summary
from prometheus_client.core import CollectorRegistry
import prometheus_client
import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import json

app = FastAPI()
@app.get('/metrics', response_class=PlainTextResponse)
def get_data():
    data_str = '[{"index":"flash-openapi-prod-2024-02-16-14","shard":"0","prirep":"p","state":"STARTED","docs":"2924399","store":"3040","ip":"10.62.217.39","node":"node-hot-temp"},{"index":"flash-openapi-prod-2024-02-16-14","shard":"0","prirep":"r","state":"STARTED","docs":"2924399","store":"3041","ip":"10.62.217.40","node":"node-hot-06"},{"index":"flash-openapi-prod-2024-02-16-14","shard":"1","prirep":"r","state":"STARTED","docs":"2927042","store":"3042","ip":"10.62.217.39","node":"node-hot-temp"}]'
    data_arr = json.loads(data_str)
    REGISTRY = CollectorRegistry(auto_describe=False)
    opensearch_shards_docs = Gauge("opensearch_shards_docs", "OpenSearch Shards Docs Count", ["index", "shard", "prirep", "ip", "node"], registry=REGISTRY)
    opensearch_shards_size = Gauge("opensearch_shards_size", "OpenSearch Shards Size", ["index", "shard", "prirep", "ip", "node"], registry=REGISTRY)
    for item in data_arr:
        opensearch_shards_docs.labels(item['index'],item['shard'],item['prirep'],item['ip'],item['node']).set(item['docs'])
    for item in data_arr:
        opensearch_shards_size.labels(item['index'],item['shard'],item['prirep'],item['ip'],item['node']).set(item['store'])
    return prometheus_client.generate_latest(REGISTRY)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9330, log_level="info")