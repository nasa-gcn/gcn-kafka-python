from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import jwt


def test_oidc_with_file(monkeypatch):
    mock_fetch_token = MagicMock(
        return_value={
            "access_token": jwt.encode({"exp": 1234567890}, "secret", algorithm="HS256")
        }
    )
    mock_session_instance = MagicMock(refresh_token=mock_fetch_token)
    mock_session_class = MagicMock(return_value=mock_session_instance)
    monkeypatch.setattr("gcn_kafka.oidc.OAuth2Session", mock_session_class)

    # Setup config
    config = {
        "sasl.oauthbearer.client.id": "client_id",
        "sasl.oauthbearer.scope": "my/scope",
        "sasl.oauthbearer.token.endpoint.url": "https://example.com/token",
    }

    fake_home = Path("/fake/home")
    fake_token = "fake-refresh-token"
    with patch("pathlib.Path.home", return_value=fake_home):
        with patch("builtins.open", mock_open(read_data=fake_token)) as m_open:
            from gcn_kafka.oidc import set_oauth_cb

            set_oauth_cb(config)

            oauth_cb = config.pop("oauth_cb")
            assert config == {}

            token, exp = oauth_cb()

            # Check file was opened at the correct path
            expected_file = fake_home.joinpath(".gcn", "my_scope")
            m_open.assert_called_once_with(expected_file, "r")

            # Check OAuth2Session was used correctly
            mock_fetch_token.assert_called_once_with(
                "https://example.com/token", "fake-refresh-token"
            )
            assert isinstance(token, str)
            assert exp == jwt.decode(token, options={"verify_signature": False})["exp"]
