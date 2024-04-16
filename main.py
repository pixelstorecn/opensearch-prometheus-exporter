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
import os
import re

opensearch_address = os.getenv('OPENSEARCH_ADDRESS')
opensearch_username = os.getenv('OPENSEARCH_USERNAME')
opensearch_password = os.getenv('OPENSEARCH_PASSWORD')

app = FastAPI()
@app.get('/metrics', response_class=PlainTextResponse)
def get_data():
    
    es_cluster_addr = "http://"+opensearch_address+":9200/_cat/health?format=json"
    cluster_str = rq.get(es_cluster_addr, auth=(opensearch_username, opensearch_password))
    cluster_arr = json.loads(cluster_str.content)
    cluster = cluster_arr[0]["cluster"]
    
    es_shards_addr = "http://"+opensearch_address+":9200/_cat/shards?format=json&bytes=mb"
    data_str = rq.get(es_shards_addr, auth=(opensearch_username, opensearch_password))
    data_arr = json.loads(data_str.content)
    REGISTRY = CollectorRegistry(auto_describe=False)
    opensearch_shards_docs = Gauge("opensearch_shards_docs", "OpenSearch Shards Docs Count", ["index", "shard", "prirep", "instance_ip", "node", "shortname", "cluster"], registry=REGISTRY)
    opensearch_shards_size = Gauge("opensearch_shards_size", "OpenSearch Shards Size", ["index", "shard", "prirep", "instance_ip", "node", "shortname", "cluster"], registry=REGISTRY)
    for item in data_arr:
        pattern_hour = r"^([a-zA-Z-]*)-([0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2})$"
        pattern_day = r"^([a-zA-Z-_]*)-([0-9]{4}-[0-9]{2}-[0-9]{2})$"
        pattern_day2 = r"^([a-zA-Z-_]*)-([0-9]{8})$"
        pattern_month = r"^([a-zA-Z-]*)-([0-9]{4}-[0-9]{2})$"
        if item['docs'] != None:
            item_index = item['index']
            if re.search(pattern_hour, item_index):
                shortname = item_index[:-14]
            elif re.search(pattern_day, item_index):
                shortname = item_index[:-11]
            elif re.search(pattern_day2, item_index):
                shortname = item_index[:-9]
            elif re.search(pattern_month, item_index):
                shortname = item_index[:-8]
            else:
                shortname = item_index
            opensearch_shards_docs.labels(item['index'],item['shard'],item['prirep'],item['ip'],item['node'],shortname,cluster).set(item['docs'])
    for item in data_arr:
        pattern_hour = r"^([a-zA-Z-]*)-([0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2})$"
        pattern_day = r"^([a-zA-Z-_]*)-([0-9]{4}-[0-9]{2}-[0-9]{2})$"
        pattern_day2 = r"^([a-zA-Z-_]*)-([0-9]{8})$"
        pattern_month = r"^([a-zA-Z-]*)-([0-9]{4}-[0-9]{2})$"
        if item['store'] != None:
            item_index = item['index']
            if re.search(pattern_hour, item_index):
                shortname = item_index[:-14]
            elif re.search(pattern_day, item_index):
                shortname = item_index[:-11]
            elif re.search(pattern_day2, item_index):
                shortname = item_index[:-9]
            elif re.search(pattern_month, item_index):
                shortname = item_index[:-8]
            else:
                shortname = item_index
            opensearch_shards_size.labels(item['index'],item['shard'],item['prirep'],item['ip'],item['node'],shortname,cluster).set(item['store'])
    return prometheus_client.generate_latest(REGISTRY)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9330, log_level="info")
