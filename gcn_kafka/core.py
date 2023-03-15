# SPDX-License-Identifier: CC0-1.0

from typing import Any, Mapping, Optional, Union
try:
    from typing import Literal
except ImportError:
    # FIXME: Remove once we drop support for Python 3.7.
    from typing_extensions import Literal
from uuid import uuid4

import certifi
import confluent_kafka
import confluent_kafka.admin
from jsonschema import validate, exceptions
import json
import requests

from oidc import set_oauth_cb


def get_config(mode, config, **kwargs):
    # Merge configuration from user.
    config = update_config(config, **kwargs)

    # SSL configuration.
    if config.setdefault("security.protocol", "sasl_ssl") == "sasl_ssl":
        if not config.get("ssl.ca.location"):
            # confluent-kafka wheels are statically linked against openssl,
            # but _that_ version of openssl may expect to find the CA cert
            # bundle at a different location than the users's system. Provide
            # certificate bundle from Certifi.
            config["ssl.ca.location"] = certifi.where()

    domain = config.pop("domain", "gcn.nasa.gov")
    client_id = config.pop("client_id", None)
    client_secret = config.pop("client_secret", None)

    config.setdefault("bootstrap.servers", f"kafka.{domain}")

    if client_id:
        # Configure authentication and authorization using OpenID Connect.
        config.setdefault("sasl.mechanisms", "OAUTHBEARER")
        config.setdefault("sasl.oauthbearer.method", "oidc")
        config.setdefault("sasl.oauthbearer.client.id", client_id)
        if client_secret:
            config.setdefault("sasl.oauthbearer.client.secret", client_secret)
        config.setdefault(
            "sasl.oauthbearer.token.endpoint.url",
            f"https://auth.{domain}/oauth2/token")

    if mode == "consumer" and not config.get("group.id"):
        config["group.id"] = str(uuid4())

    if mode == "producer":
        config.setdefault('compression.type', 'zstd')

    set_oauth_cb(config)
    return config


def update_config(config, **kwargs):
    result = dict(config or {})
    result.update({k: v for k, v in kwargs.items() if v is not None})
    return result


class Producer(confluent_kafka.Producer):
    def __init__(
        self,
        config: Optional[Mapping[str, Any]] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        domain: Optional[
            Union[
                Literal["gcn.nasa.gov"],
                Literal["test.gcn.nasa.gov"],
                Literal["dev.gcn.nasa.gov"],
            ]
        ] = None,
        **kwargs,
    ):
        super().__init__(
            get_config(
                "producer",
                config,
                client_id=client_id,
                client_secret=client_secret,
                domain=domain,
                **kwargs,
            )
        )
        # Workaround for https://github.com/edenhill/librdkafka/issues/3871.
        # FIXME: Remove once fixed upstream, or on removal of oauth_cb.
        self.poll(0)


    def produce(self, topic, data):
        try:
            request = requests.get(data['$schema'])
            schema_model = json.loads(request.content.decode())
            validate(data, schema_model)
        except exceptions.ValidationError:
            print("The instance of the data provided is invalid against the schema")
            return
        except exceptions.SchemaError:
            print("The provided schema is invalid")
            return
        
        notice_id = str(uuid4())
        data['notice_id'] = notice_id
        
        super().produce(topic, json.dumps(data))
        print(f'Successfully posted topic with notice id: {notice_id}')
        

class Consumer(confluent_kafka.Consumer):
    def __init__(
        self,
        config: Optional[Mapping[str, Any]] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        domain: Optional[
            Union[
                Literal["gcn.nasa.gov"],
                Literal["test.gcn.nasa.gov"],
                Literal["dev.gcn.nasa.gov"],
            ]
        ] = None,
        **kwargs,
    ):
        super().__init__(
            get_config(
                "consumer",
                config,
                client_id=client_id,
                client_secret=client_secret,
                domain=domain,
                **kwargs,
            )
        )
        # Workaround for https://github.com/edenhill/librdkafka/issues/3871.
        # FIXME: Remove once fixed upstream, or on removal of oauth_cb.
        self.poll(0)


class AdminClient(confluent_kafka.admin.AdminClient):
    def __init__(
        self,
        config: Optional[Mapping[str, Any]] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        domain: Optional[
            Union[
                Literal["gcn.nasa.gov"],
                Literal["test.gcn.nasa.gov"],
                Literal["dev.gcn.nasa.gov"],
            ]
        ] = None,
        **kwargs,
    ):
        super().__init__(
            get_config(
                "admin",
                config,
                client_id=client_id,
                client_secret=client_secret,
                domain=domain,
                **kwargs,
            )
        )
        # Workaround for https://github.com/edenhill/librdkafka/issues/3871.
        # FIXME: Remove once fixed upstream, or on removal of oauth_cb.
        self.poll(0)
