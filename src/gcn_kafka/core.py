# SPDX-License-Identifier: CC0-1.0

from typing import Any, Literal, Mapping, Optional, Union
from uuid import uuid4

import certifi
import confluent_kafka
import confluent_kafka.admin

from .oidc import set_oauth_cb


def get_config(mode, scope, config, **kwargs):
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
    config.setdefault("bootstrap.servers", f"kafka.{domain}")

    if client_id:
        config.setdefault("sasl.mechanisms", "OAUTHBEARER")
        config.setdefault("sasl.oauthbearer.client.id", client_id)
        config.setdefault(
            "sasl.oauthbearer.token.endpoint.url", f"https://auth.{domain}/oauth2/token"
        )
        config.setdefault("sasl.oauthbearer.scope", scope)

    if mode == "consumer" and not config.get("group.id"):
        config["group.id"] = str(uuid4())

    if mode == "producer":
        config.setdefault("compression.type", "zstd")

    set_oauth_cb(config)
    return config


def update_config(config, **kwargs):
    result = dict(config or {})
    result.update({k: v for k, v in kwargs.items() if v is not None})
    return result


class Producer(confluent_kafka.Producer):
    def __init__(
        self,
        scope: Optional[str] = None,  # Maybe these should be required?
        config: Optional[Mapping[str, Any]] = None,
        client_id: Optional[str] = None,
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
                scope,
                config,
                client_id=client_id,
                domain=domain,
                **kwargs,
            )
        )
        # Workaround for https://github.com/confluentinc/librdkafka/issues/3753#issuecomment-1058272987.
        # FIXME: Remove once fixed upstream, or on removal of oauth_cb.
        self.poll(0)


class Consumer(confluent_kafka.Consumer):
    def __init__(
        self,
        scope: Optional[str] = None,  # Maybe these should be required?
        config: Optional[Mapping[str, Any]] = None,
        client_id: Optional[str] = None,
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
                scope,
                config,
                client_id=client_id,
                domain=domain,
                **kwargs,
            )
        )
        # Workaround for https://github.com/confluentinc/librdkafka/issues/3753#issuecomment-1058272987.
        # FIXME: Remove once fixed upstream, or on removal of oauth_cb.
        self.poll(0)


class AdminClient(confluent_kafka.admin.AdminClient):
    def __init__(
        self,
        config: Optional[Mapping[str, Any]] = None,
        client_id: Optional[str] = None,
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
                scope="gcn.nasa.gov/kafka-admin",
                client_id=client_id,
                domain=domain,
                **kwargs,
            )
        )
        # Workaround for https://github.com/confluentinc/librdkafka/issues/3753#issuecomment-1058272987.
        # FIXME: Remove once fixed upstream, or on removal of oauth_cb.
        self.poll(0)
