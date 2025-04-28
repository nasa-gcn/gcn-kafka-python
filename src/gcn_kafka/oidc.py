# SPDX-License-Identifier: CC0-1.0
from pathlib import Path

import jwt
from authlib.integrations.requests_client import OAuth2Session


def set_oauth_cb(config):
    """Implement client support for KIP-768 OpenID Connect.

    Apache Kafka 3.1.0 supports authentication using OpenID Client Credentials.
    Native support for Python is still incomplete due to this issue:
    https://github.com/confluentinc/librdkafka/issues/3751

    Meanwhile, this is a pure Python implementation of the refresh token
    callback.
    """

    client_id = config.pop("sasl.oauthbearer.client.id")

    client = OAuth2Session(client_id=client_id)
    scope = config.pop("sasl.oauthbearer.scope")
    url = config.pop("sasl.oauthbearer.token.endpoint.url")

    def refresh_cognito_tokens():
        home = Path.home()
        with open(home.joinpath(".gcn", scope.replace("/", "_")), "r") as file:
            token = file.read()
        newToken = client.refresh_token(url, token)
        return newToken

    def oauthbearer_token_refresh_cb(*_, **__):
        token_info = refresh_cognito_tokens()
        jwt_token = token_info["access_token"]
        decoded = jwt.decode(jwt_token, options={"verify_signature": False})
        exp = decoded["exp"]
        return jwt_token, exp

    config["oauth_cb"] = oauthbearer_token_refresh_cb
