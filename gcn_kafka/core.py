# SPDX-License-Identifier: CC0-1.0

import os
import re
from typing import Any, Mapping, Optional, Union
try:
    from typing import Literal
except ImportError:
    # FIXME: Remove once we drop support for Python 3.7.
    from typing_extensions import Literal
from uuid import uuid4

import certifi
import confluent_kafka

from .oidc import set_oauth_cb


def get_config(mode, config, **kwargs):
    # Merge configuration from user.
    config = {**(config or {}), **kwargs}

    # SSL configuration.
    if config.setdefault("security.protocol", "sasl_ssl") == "sasl_ssl":
        if not config.get("ssl.ca.location"):
            # confluent-kafka wheels are statically linked against openssl,
            # but _that_ version of openssl may expect to find the CA cert
            # bundle at a different location than the users's system. Provide
            # certificate bundle from Certifi.
            config["ssl.ca.location"] = certifi.where()

    domain = config.pop("domain", None)
    client_id = config.pop("client_id", None)
    client_secret = config.pop("client_secret", None)

    if domain:
        config.setdefault("bootstrap.servers", f"kafka.{domain}")

    if client_id:
        # Configure authentication and authorization using OpenID Connect.
        config.setdefault("sasl.mechanisms", "OAUTHBEARER")
        config.setdefault("sasl.oauthbearer.method", "oidc")
        config.setdefault("sasl.oauthbearer.client.id", client_id)
        if client_secret:
            config.setdefault("sasl.oauthbearer.client.secret", client_secret)
        if domain:
            config.setdefault(
                "sasl.oauthbearer.token.endpoint.url",
                f"https://auth.{domain}/oauth2/token",
            )

    if mode == "consumer" and not config.get("group.id"):
        config["group.id"] = str(uuid4())

    set_oauth_cb(config)
    return config

env_key_splitter = re.compile(r'_+')
replacement_dict = {'_': '.', '__': '-', '___': '_'}

def replacement(match: re.Match) -> str:
    text = match[0]
    return replacement_dict.get(text) or text


def config_from_env(env: dict[str, str], prefix: str = 'KAFKA_') -> dict[str, str]:
    """Construct a Kafka client configuration dictionary from env variables.
    This uses the same rules as
    https://docs.confluent.io/platform/current/installation/docker/config-reference.html
    to convert from configuration variables to environment variable names:
    * Start the environment variable name with the given prefix.
    * Convert to upper-case.
    * Replace periods (`.`) with single underscores (`_`).
    * Replace dashes (`-`) with double underscores (`__`).
    * Replace underscores (`-`) with triple underscores (`___`).
    """
    config = {}
    for key, value in env.items():
        if key.startswith(prefix):
            key = env_key_splitter.sub(replacement, key.removeprefix(prefix))
            config[key.lower()] = value
    return config


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
        ] = 'gcn.nasa.gov',
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
        # Workaround for https://github.com/edenhill/librdkafka/issues/3263.
        # FIXME: Remove once confluent-kafka-python 1.9.0 has been released.
        self.poll(0)


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
        ] = 'gcn.nasa.gov',
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
        # Workaround for https://github.com/edenhill/librdkafka/issues/3263.
        # FIXME: Remove once confluent-kafka-python 1.9.0 has been released.
        self.poll(0)
