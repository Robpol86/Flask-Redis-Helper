from flask import current_app
import pytest

from flask.ext.redis import Redis


class FakeApp(object):
    config = dict()
    static_url_path = ''

    def register_blueprint(self, _):
        pass


def test_multiple():
    assert 'redis' in current_app.extensions

    with pytest.raises(ValueError):
        Redis(current_app)


def test_one_dumb_line():
    app = FakeApp()
    Redis(app)
    assert 'redis' in app.extensions
