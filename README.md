Flask-Redis-Helper
==================

Yet another Redis extension for Flask. `Flask-Redis-Helper` doesn't break PyCharm autocomplete/inspections and handles
the Flask application context the same way SQLAlchemy does.

Attribution
-----------

Inspired by [Flask-SQLAlchemy](http://pythonhosted.org/Flask-SQLAlchemy/) and
[Flask-And-Redis](https://github.com/playpauseandstop/Flask-And-Redis).

Supported Platforms
-------------------

* OSX and Linux.
* Python 2.7
* [Flask](http://flask.pocoo.org/) 0.10.1
* [Redis](http://redis.io/) 2.9.1
* [Celery](http://www.celeryproject.org/) 3.1.11

Probably works on other versions too.

Quickstart
----------

Install:
```bash
pip install Flask-Redis-Helper
```

Example:
```python
from flask import Flask
from flask.ext.redis import Redis

app = Flask(__name__)
app.config['REDIS_URL'] = 'redis://localhost'
redis = Redis(app)
```

Factory Example
---------------

```python
# extensions.py
from flask.ext.redis import Redis

redis = Redis()
redis_cache = Redis()
```

```python
# application.py
from flask import Flask
from extensions import redis, redis_cache

def create_app():
    app = Flask(__name__)
    app.config['REDIS_URL'] = 'redis://localhost/0'
    app.config['REDIS_CACHE_URL'] = 'redis://localhost/1'
    redis.init_app(app)
    redis_cache.init_app(app, config_prefix='REDIS_CACHE')
    return app
```

```python
# manage.py
from application import create_app

app = create_app()
app.run()
```

Configuration
-------------

`Flask-Redis-Helper` subclasses `StrictRedis` and adds the init_app() method for delayed initialization (for 
applications that instantiate extensions in a separate file, but run init_app() in the same file Flask() was 
instantiated).

The following config settings are searched for in the Flask application's configuration dictionary:
* `REDIS_URL` -- URL to Redis server. May be a network URL or Unix socket URL. Individual components may be overridden
  by settings below (like setting REDIS_DB). URLs must start with redis://, file://, or redis+socket:// (Celery
  compatibility). redis:// handles ambiguous URLs (like redis://localhost and redis://my_socket_file) by
  prioritizing network URL interpretations over socket URLs. Use the file:// or redis+socket:// URL schemes to
  force socket URL interpretations over network URLs.
* `REDIS_SOCKET` -- UNIX socket file path. If specified, disables REDIS_HOST and REDIS_PORT settings.
* `REDIS_HOST` -- the Redis server's hostname/IP. Default is localhost.
* `REDIS_PORT` -- TCP port number. Default is 6379.
* `REDIS_PASSWORD` -- password. Default is None.
* `REDIS_DB` -- DB instance (e.g. 1). Must be an integer. Default is 0.
