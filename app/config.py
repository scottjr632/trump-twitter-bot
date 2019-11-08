import os
import logging

config = {
    "development": "app.settings.DevelopmentConfig",
    "testing": "app.settings.TestingConfig",
    "default": "app.settings.DevelopmentConfig",
    "production": "app.settings.ProductionConfig"
}


def _validate_config_status(status: str, default='default') -> str:
    to_validate = config.get(status)
    if to_validate is None:
        logging.warning('Unable to find status: %s. Using default config.' % status)
        return config.get(default)

    return to_validate


def configure_app(app, status='default'):
    app.config.from_object(_validate_config_status(status))
