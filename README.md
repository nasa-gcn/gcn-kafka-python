[![PyPI](https://img.shields.io/pypi/v/gcn-kafka)](https://pypi.org/project/gcn-kafka/)

# GCN Kafka Client for Python

This is the official Python client for the [General Coordinates Network (GCN)](https://gcn.nasa.gov). It is a very lightweight wrapper around [confluent-kafka-python](https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html).

## To Install

Run this command to install with [pip](https://pip.pypa.io/):

```
pip install gcn-kafka
```

or this command to install with with [conda](https://docs.conda.io/):

```
conda install -c conda-forge gcn-kafka
```

## To Use

Create a consumer.

```python
from gcn_kafka import Consumer
consumer = Consumer(client_id='fill me in',
                    client_secret='fill me in')
```

List all topics:

```python
print(consumer.list_topics().topics)
```

Subscribe to topics and receive alerts:

```python
consumer.subscribe(['gcn.classic.text.FERMI_GBM_FIN_POS',
                    'gcn.classic.text.LVC_INITIAL'])
while True:
    for message in consumer.consume():
        print(message.value())
```

## Testing and Development Kafka Clusters

GCN has three Kafka clusters: production, testing, and an internal development deployment. Use the optional ``domain`` keyword argument to select which broker to connect to.

```python
# Production (default)
consumer = Consumer(client_id='fill me in',
                    client_secret='fill me in',
                    domain='gcn.nasa.gov')

# Testing
consumer = Consumer(client_id='fill me in',
                    client_secret='fill me in',
                    domain='test.gcn.nasa.gov')

# Development (internal)
consumer = Consumer(client_id='fill me in',
                    client_secret='fill me in',
                    domain='dev.gcn.nasa.gov')
```
