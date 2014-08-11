from flask import Flask
import pytest

from flask.ext.redis import Redis


@pytest.fixture(autouse=True, scope='session')
def app_context(request):
    """Initialize the Flask application for tests."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    Redis(app)
    context = app.app_context()
    context.push()
    request.addfinalizer(lambda: context.pop())
