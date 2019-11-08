import pytest

from app import app
from app.config import configure_app


@pytest.fixture(scope='module')
def test_client():
    configure_app(app, status='testing')

    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = app.test_client()

    # Establish an application context before running the tests.
    ctx = app.app_context()
    APP_CONTEXT = ctx
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()
