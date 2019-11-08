import pytest

from app.config import _validate_config_status, config

DEFAULT_CONFIG = config.get('default')


def test_validate_config_status_returns_default():
    non_valid_name = 'I am not a valid config'
    with pytest.raises(KeyError):
        config[non_valid_name]
    
    app_config = _validate_config_status(non_valid_name)
    assert app_config == DEFAULT_CONFIG


def test_validate_config_status_returns_valid():
    valid_name = 'testing'
    assert config.get(valid_name) is not None

    app_config = _validate_config_status(valid_name)
    assert app_config == config.get(valid_name)
