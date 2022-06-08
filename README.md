# GCN Kafka Client for Python

This is the official Python client for the [General Coordinates Network (GCN)](https://gcn.nasa.gov). It is a very lightweight wrapper around [confluent-kafka-python](https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html).

## To Install

Run this command to install with [pip](https://pip.pypa.io/):

```
pip install gcn-kafka
```

## To use

Create a consumer:

```pycon
>>> from gcn_kafka import Consumer
>>> consumer = Consumer(client_id='fill me in', client_secret='fill me in')
```

List all topics:

```pycon
>>> print(consumer.list_topics().topics)
{'gcn.classic.text.CALET_GBM_FLT_LC': TopicMetadata(gcn.classic.text.CALET_GBM_FLT_LC, 1 partitions), 'gcn.classic.voevent.FERMI_GBM_SUBTHRESH': TopicMetadata(gcn.classic.voevent.FERMI_GBM_SUBTHRESH, 1 partitions), ...}
```

Subscribe to topics and receive alerts:

```pycon
>>> consumer.subscribe(['gcn.classic.text.FERMI_GBM_FIN_POS', 'gcn.classic.text.LVC_INITIAL'])
>>> while True:
... for message in consumer.consume():
...     print(message.value())
```