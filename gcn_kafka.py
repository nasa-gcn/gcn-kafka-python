BASE_CONFIG = {
    'bootstrap.servers': 'kafka0.dev.gcn.gsfc.nasa.gov:9093',
    'sasl.mechanisms': 'OAUTHBEARER',
    'sasl.oauthbearer.method': 'oidc',
    'sasl.oauthbearer.scope': 'gcn-tokens/kafka-consumer',
    'sasl.oauthbearer.token.endpoint.url': 'https://gcn-tokens.auth.us-east-1.amazoncognito.com/oauth2/token',
    'security.protocol': 'sasl_ssl',
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
