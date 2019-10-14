import os

config = {
    "development": "app.settings.DevelopmentConfig",
    "testing": "app.settings.TestingConfig",
    "default": "app.settings.DevelopmentConfig",
    "production": "app.settings.ProductionConfig"
}


def configure_app(app, status="default"):
    app.config.from_object(config[status])