[![PyPI](https://img.shields.io/pypi/v/gcn-kafka)](https://pypi.org/project/gcn-kafka/)
[![codecov](https://codecov.io/gh/nasa-gcn/gcn-kafka-python/branch/main/graph/badge.svg?token=KSFUD0LETW)](https://codecov.io/gh/nasa-gcn/gcn-kafka-python)

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
    for message in consumer.consume(timeout=1):
        print(message.value())
```

The `timeout` argument to `consume()`, given as an integer number of seconds,
will allow the program to exit quickly once it has reached the end of the
existing message buffer. This is useful for users who just want to recover an
older message from the stream. `timeout` will also make the `while True`
infinite loop interruptible via the standard ctrl-c key sequence, which
`consume()` ignores.

## Testing and Development Kafka Clusters

GCN has three Kafka clusters: production, testing, and an internal development deployment. Use the optional `domain` keyword argument to select which broker to connect to.

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

## FAQ

**How can I keep track of the last read message when restarting a client?**

A key feature of kafka consumer clients is the ability to perform persistent tracking of which messages have been read. This allows clients to recover missed messages after a   restart by beginning at the earliest unread message rather than the next available message from the stream. In order to enable this feature, you will need to set a client Group ID using the configuration dictionary argument for the Consumer class as well as change the auto offset reset option to the ‘earliest’ setting. Once this is done, every new client with the given Group ID will begin reading the specified topic at the earliest unread message. When doing this, it is recommended to turn OFF the auto commit feature because it can lose track of the last read message if the client crashes before the auto commit interval (5 seconds by default) occurs. Manually committing messages (i.e. storing the state of the last read message) once they are read is the most robust method for tracking the last read message.

Example code: 
```python3
from gcn_kafka import Consumer

config = {'group.id': 'my group name',
          'auto.offset.reset': 'earliest',
          'enable.auto.commit': False}

consumer = Consumer(config=config,
                    client_id='fill me in',
                    client_secret='fill me in',
                    domain='gcn.nasa.gov')

topics = ['gcn.classic.voevent.FERMI_GBM_SUBTHRESH']
consumer.subscribe(topics)

while True:
    for message in consumer.consume(timeout=1):
        print(message.value())
        consumer.commit(message)
```

**How can I read messages beginning at the earliest available messages for a given stream?**

You can begin reading a given topic stream from the earliest message that is present in the stream buffer by setting the Group ID to an empty string and applying the ‘earliest’ setting for the auto offset reset option in the configuration dictionary argument for the Consumer class. This feature allows the user to scan for older messages for testing purposes or to recover messages that may have been missed due to a crash or network outage. Just keep in mind that the stream buffers are finite in size. They currently hold messages from the past few days.

Example code:
```python3
from gcn_kafka import Consumer

config = {'auto.offset.reset': 'earliest'}

consumer = Consumer(config=config,
                    client_id='fill me in',
                    client_secret='fill me in',
                    domain='gcn.nasa.gov')

topics = ['gcn.classic.voevent.INTEGRAL_SPIACS']
consumer.subscribe(topics)

while True:
    for message in consumer.consume(timeout=1):
        print(message.value())
```

**How can I search for messages occurring within a given date range?**

To search for messages in a given date range, you can use the `offsets_for_times()` function from the Consumer class to get the message offsets for the desired date range. You can then assign the starting offset to the Consumer and read the desired number of messages. When doing so, keep in mind that the stream buffers are finite in size. It is not possible to recover messages prior to the start of the stream buffer. The GCN stream buffers are currently set to hold messages from the past few days.

Example code:
```python3
import datetime
from gcn_kafka import Consumer
from confluent_kafka import TopicPartition

consumer = Consumer(client_id='fill me in',
                    client_secret='fill me in',
                    domain='gcn.nasa.gov')

# get messages occurring 3 days ago
timestamp1 = int((datetime.datetime.now() - datetime.timedelta(days=3)).timestamp() * 1000)
timestamp2 = timestamp1 + 86400000 # +1 day

topic = 'gcn.classic.voevent.INTEGRAL_SPIACS'
start = consumer.offsets_for_times(
    [TopicPartition(topic, 0, timestamp1)])
end = consumer.offsets_for_times(
    [TopicPartition(topic, 0, timestamp2)])

consumer.assign(start)
for message in consumer.consume(end[0].offset - start[0].offset, timeout=1):
    print(message.value())
```
