# SPDX-License-Identifier: CC0-1.0

from typing import Any, Literal, Mapping, Optional, Union
from uuid import uuid4

import certifi
import confluent_kafka
import confluent_kafka.admin


def get_config(mode, config, **kwargs):
    # Merge configuration from user.
    config = update_config(config, **kwargs)

    # SSL configuration.
    if config.setdefault("security.protocol", "sasl_ssl") == "sasl_ssl":
        # confluent-kafka wheels are statically linked against openssl,
        # but _that_ version of openssl may expect to find the CA cert
        # bundle at a different location than the users's system. Provide
        # certificate bundle from Certifi.
        default_cert_location = certifi.where()
        config.setdefault("ssl.ca.location", default_cert_location)
        config.setdefault("https.ca.location", default_cert_location)

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
            "sasl.oauthbearer.token.endpoint.url", f"https://auth.{domain}/oauth2/token"
        )

    if mode == "consumer" and not config.get("group.id"):
        config["group.id"] = str(uuid4())

    if mode == "producer":
        config.setdefault("compression.type", "zstd")

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
