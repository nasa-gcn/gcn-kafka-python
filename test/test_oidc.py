from unittest.mock import MagicMock

from gcn_kafka import oidc


def test_no_oidc():
    config = {}
    oidc.set_oauth_cb(config)
    assert config == {}


def test_oidc(monkeypatch):
    mock_session_class = MagicMock()
    monkeypatch.setattr(oidc, "OAuth2Session", mock_session_class)

    config = {
        "sasl.oauthbearer.method": "oidc",
        "sasl.oauthbearer.client.id": "client_id",
        "sasl.oauthbearer.client.secret": "client_secret",
        "sasl.oauthbearer.scope": "scope",
        "sasl.oauthbearer.token.endpoint.url": "token_endpoint",
    }
    oidc.set_oauth_cb(config)

    oauth_cb = config.pop("oauth_cb")
    assert config == {}
    mock_session_class.assert_called_once_with(
        "client_id", "client_secret", scope="scope"
    )
    oauth_cb()
    mock_session_class.return_value.fetch_token.assert_called_once_with(
        "token_endpoint", grant_type="client_credentials"
    )
