# SPDX-License-Identifier: CC0-1.0


def set_oauth_cb(config, scope, client_id):
    """Implement client support for KIP-768 OpenID Connect.

    Apache Kafka 3.1.0 supports authentication using OpenID Client Credentials.
    Native support for Python is still incomplete due to this issue:
    https://github.com/confluentinc/librdkafka/issues/3751

    Meanwhile, this is a pure Python implementation of the refresh token
    callback.
    """

    def refresh_cognito_tokens():
        url = config["sasl.oauthbearer.token.endpoint.url"]

        home = Path.home()
        with open(home.joinpath(".gcn", scope.replace("/", "_")), "r") as file:
            token = file.read()

        data = {
            "grant_type": "refresh_token",
            "client_id": client_id,  # Public ClientID
            "refresh_token": token,
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = requests.post(url, data=data, headers=headers)
        response.raise_for_status()

        return response.json()

    def oauthbearer_token_refresh_cb(*_, **__):
        token_info = refresh_cognito_tokens()
        jwt_token = token_info["access_token"]
        decoded = jwt.decode(jwt_token, options={"verify_signature": False})
        exp = decoded["exp"]
        return jwt_token, exp

    config["oauth_cb"] = oauthbearer_token_refresh_cb
