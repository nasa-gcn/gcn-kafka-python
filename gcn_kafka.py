# Self-signed SSL/TLS certificate of the Kafka broker.
# FIXME: Remove this once the broker has a certificate signed by CA.
CERT = """\
-----BEGIN CERTIFICATE-----
MIIDEjCCAfqgAwIBAgIUFE92vLqgb0ZV40K6iGYhHdVX0kkwDQYJKoZIhvcNAQEL
BQAwJzElMCMGA1UEAwwcaXAtMTAtNTEtNjAtMjQxLmVjMi5pbnRlcm5hbDAeFw0y
MjAxMTkxNTUwNDZaFw0zMjAxMTcxNTUwNDZaMCcxJTAjBgNVBAMMHGlwLTEwLTUx
LTYwLTI0MS5lYzIuaW50ZXJuYWwwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEK
AoIBAQC53KrGL4SGGoKqCE+aAh5EheyQMHBs4WGBoVqKgHReOZ5+1qonSw1W5I53
912ay9U1Pp8oHil5AuixSB1RF7UFd4ma7GbmdI0wrM2uwR0qbtfcjx4sK2aOVgwL
QIw6uBmYxaj8LKoVd5ugH7Hjfs1cs9BIj3mgWePXIx0XPK/oNHCYTNjh2yhdkQOv
0SPTzH2eE6n/ZN1TMs+2KeGoZahwepdQJOb/pWDyxT5E+j6png3P6opA70aPGYkD
4PpcmDL17gow3dPnQAwa/XHoqr0VqV4NM55F3owV8DBPAzAUBmNGK/9L5PFoICs4
bTOu2ZA2b+zulIJFX+jiCzjkGGYxAgMBAAGjNjA0MAkGA1UdEwQCMAAwJwYDVR0R
BCAwHoIcaXAtMTAtNTEtNjAtMjQxLmVjMi5pbnRlcm5hbDANBgkqhkiG9w0BAQsF
AAOCAQEAiFisrnMqK5KGXuoMmkSb4IHppAwsdWea++bn9McSsf9Pcgwd6+Xe293Y
PuUDueEZcUuivfUYKN8TqwogqIvmIz/ckQIIdZQA1guhf9q6YQpt4iFND9YUI/2i
PRWrxHiftqNQNiI5IwBQk9S4ogoQHD5OtAt1SgX4oFO1lg1mxAC/Yvb17FUvay6t
DUm0XwiQLLQ2vPvTKB0tbFqAtBNErNKoG3lGmeAaCjIPUPB/+r8gQy0Fb8UTYMK1
2vXk/ieTSGwmtH9Z3iakfba+x5G5JZWeppL+dO28GttEJqjX+r/bNrwY8+9MDUoq
aGCCAd3F/zQMbO/SQrtCEYJ7U8MQ/A==
-----END CERTIFICATE-----
"""


BASE_CONFIG = {
    'bootstrap.servers': 'kafka0.dev.gcn.gsfc.nasa.gov:9093',
    'sasl.mechanisms': 'OAUTHBEARER',
    'sasl.oauthbearer.extensions': ' ',  # FIXME: must not be blank
    'sasl.oauthbearer.method': 'oidc',
    'sasl.oauthbearer.scope': 'gcn-tokens/kafka-consumer',
    'sasl.oauthbearer.token.endpoint.url': 'https://gcn-tokens.auth.us-east-1.amazoncognito.com/oauth2/token',
    'security.protocol': 'sasl_ssl',
    'ssl.ca.pem': CERT,
}


def get_config(client_id, client_secret):
    """Get the confluent-kafka configuration for connecting to GCN.

    Parameters
    ----------
    client_id : str
        The client ID of the application.
    client_secret : str
        The client secret of the application.

    Returns
    -------
    dict
        Configuration dictionary for :class:`confluent_kafka.Consumer` or
        `confluent_kafka.Producer`.
    """
    return {
        **BASE_CONFIG,
        'sasl.oauthbearer.client.id': client_id,
        'sasl.oauthbearer.client.secret': client_secret,
    }
