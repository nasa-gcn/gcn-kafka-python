from ..core import update_config


def test_update_config_no_overwrite():
    config = {
        'client_id':'qwertyuiopasdfghjklzxcvbnm', 
        'client_secret':'qwertyuiopljhgfdsazxcvbnmlkjhgfdsaertyuio',
        'domain':'test.test.test'
    }

    newConfig = update_config(
        config, 
        client_id=None, 
        client_secret=None
    )

    assert newConfig == config


def test_update_config_with_overwrite():
    config = {
        'client_id':'qwertyuiopasdfghjklzxcvbnm', 
        'client_secret':'qwertyuiopljhgfdsazxcvbnmlkjhgfdsaertyuio',
        'domain':'test.test.test'
    }

    newConfig = update_config(
        config,
        client_id="client_id update Success",
        client_secret="client_secret update Success"
    )

    assert newConfig['client_id'] == "client_id update Success"
    assert newConfig['client_secret'] == "client_secret update Success"
