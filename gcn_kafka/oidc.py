# SPDX-License-Identifier: CC0-1.0

from authlib.integrations.requests_client import OAuth2Session


def set_oauth_cb(config):
    """Implement client support for KIP-768 OpenID Connect.

    Apache Kafka 3.1.0 supports authentication using OpenID Client Credentials.
    Native support for Python is coming in the next release of librdkafka
    (version 1.9.0). Meanwhile, this is a pure Python implementation of the
    refresh token callback.
    """
    if config.pop("sasl.oauthbearer.method", None) != "oidc":
        return

    client_id = config.pop("sasl.oauthbearer.client.id")
    client_secret = config.pop("sasl.oauthbearer.client.secret", None)
    scope = config.pop("sasl.oauthbearer.scope", None)
    token_endpoint = config.pop("sasl.oauthbearer.token.endpoint.url")

    session = OAuth2Session(client_id, client_secret, scope=scope)

    def oauth_cb(*_, **__):
        token = session.fetch_token(token_endpoint, grant_type="client_credentials")
        return token["access_token"], token["expires_at"]

    config["oauth_cb"] = oauth_cb
