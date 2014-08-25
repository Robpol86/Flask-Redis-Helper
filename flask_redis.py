"""Redis support for Flask without breaking PyCharm inspections.

https://github.com/Robpol86/Flask-Redis-Helper
https://pypi.python.org/pypi/Flask-Redis-Helper
"""

import os

from six import moves
from redis import StrictRedis

__author__ = '@Robpol86'
__license__ = 'MIT'
__version__ = '0.1.3'


def parse_url(url):
    """Parses the supplied Redis URL and returns a dict with the parsed/split data.

    For ambiguous URLs like redis://localhost and redis://my_socket_file this function will prioritize network URLs over
    socket URLs. redis://my_socket_file will be interpreted as a network URL, with the Redis server having a hostname of
    'my_socket_file'. Use the file:// or redis+socket:// (Celery compatibility) URL scheme to force socket URL
    interpretations over network URLs.

    Positional arguments:
    url -- URL to redis server. Examples are in this file's Redis class docstring under REDIS_URL.

    Returns:
    Dictionary with parsed data, compatible with StrictRedis.__init__() keyword arguments.

    Raises:
    ValueError -- if the supplies URL was malformed or invalid.
    """
    # Parse URL, make sure string is valid.
    try:
        split = moves.urllib.parse.urlsplit(url.rstrip('/'))
    except (AttributeError, TypeError) as e:
        raise ValueError('Malformed URL specified: {0}'.format(e))
    if split.scheme not in ['redis+socket', 'redis', 'file']:
        raise ValueError('Malformed URL specified.')
    scheme = split.scheme
    netloc = split.netloc
    hostname = split.hostname
    path = split.path
    password = split.password
    port = split.port

    # Handle non-socket URLs.
    if scheme == 'redis' and netloc and not netloc.endswith('.') and not netloc.endswith('@'):
        result = dict(host=hostname)
        if password:
            result['password'] = password
        if port:
            result['port'] = port
        if path:
            if not path[1:].isdigit():
                raise ValueError('Network URL path has non-digit characters: {0}'.format(path[1:]))
            result['db'] = int(path[1:])
        return result

    # Handle socket URLs.
    if port:
        raise ValueError('Socket URL looks like non-socket URL.')
    if not password:
        socket_path = '{0}{1}'.format(netloc, path)
    elif netloc.endswith('.'):
        socket_path = '{0}{1}'.format(netloc.split('@')[1], path)
    elif not path:
        socket_path = netloc.split('@')[1]
    else:
        socket_path = path

    # Catch bad paths.
    parent_dir = os.path.split(socket_path)[0]
    if parent_dir and not os.path.isdir(parent_dir):
        raise ValueError("Unix socket path's parent not a dir: {0}".format(parent_dir))

    # Finish up.
    result = dict(unix_socket_path=socket_path)
    if password:
        result['password'] = password
    return result


def read_config(config, prefix):
    """Return a StrictRedis.__init__() compatible dictionary from data in the Flask config.

    Generate a dictionary compatible with StrictRedis.__init__() keyword arguments from data in the Flask
    application's configuration values relevant to Redis.

    This is where REDIS_URL (or whatever prefix used) is parsed, by calling parse_url().

    Positional arguments:
    config -- Flask application config dict.
    prefix -- Prefix used in config key names in the Flask app's configuration.

    Returns:
    Dictionary with parsed data, compatible with StrictRedis.__init__() keyword arguments.
    """
    # Get all relevant config values from Flask application.
    suffixes = ('URL', 'SOCKET', 'HOST', 'PORT', 'PASSWORD', 'DB')
    config_url, config_socket, config_host, config_port, config_password, config_db = [
        config.get('{0}_{1}'.format(prefix, suffix)) for suffix in suffixes
    ]
    result = dict()
    # Get more values from URL if provided.
    if config_url:
        result.update(parse_url(config_url))
    # Apply other config values.
    if config_socket:
        result['unix_socket_path'] = config_socket
    else:
        if config_host:
            result['host'] = config_host
        if config_port is not None:
            result['port'] = int(config_port)
    if config_password is not None:
        result['password'] = config_password
    if config_db is not None:
        result['db'] = int(config_db)
    return result


class _RedisState(object):
    """Remembers the configuration for the (redis, app) tuple. Modeled from SQLAlchemy."""

    def __init__(self, redis_instance, app):
        self.redis = redis_instance
        self.app = app


class Redis(StrictRedis):
    """Modeled after Flask-And-Redis and SQLAlchemy.

    Relevant configuration settings from the Flask app config:
    REDIS_URL -- URL to Redis server. May be a network URL or Unix socket URL. Individual components may be overridden
        by settings below (like setting REDIS_DB). URLs must start with redis://, file://, or redis+socket:// (Celery
        compatibility). redis:// handles ambiguous URLs (like redis://localhost and redis://my_socket_file) by
        prioritizing network URL interpretations over socket URLs. Use the file:// or redis+socket:// URL schemes to
        force socket URL interpretations over network URLs.
    REDIS_SOCKET -- UNIX socket file path. If specified, disables REDIS_HOST and REDIS_PORT settings.
    REDIS_HOST -- the Redis server's hostname/IP. Default is localhost.
    REDIS_PORT -- TCP port number. Default is 6379.
    REDIS_PASSWORD -- password. Default is None.
    REDIS_DB -- DB instance (e.g. 1). Must be an integer. Default is 0.

    The above settings names are based on the default config prefix of 'REDIS'. If the config_prefix is 'REDIS_CACHE'
    for example, then REDIS_URL will be REDIS_CACHE_URL, and so on.
    """

    def __init__(self, app=None, config_prefix=None):
        """If app argument provided then initialize Redis using application config values.

        If no app argument provided you should do initialization later with init_app method.

        Call to StrictRedis.__init__() muffled by setting connection_pool to True. This prevents any real initialization
        from occurring inside StrictRedis. Once self.init_app() is called (either by providing a value for `app` in
        self.__init__() or by manually calling self.init_app() later on) StrictRedis.__init__() is called again without
        connection_pool=True, thereby doing the actual initialization after this class is instantiated.

        Keyword arguments:
        app -- Flask application instance.
        config_prefix -- Prefix used in config key names in the Flask app's configuration. More info in
            self.init_app()'s docstring.
        """
        super(Redis, self).__init__(connection_pool=True)  # Prevent StrictRedis from initializing.
        if app is not None:
            self.init_app(app, config_prefix)

    def init_app(self, app, config_prefix=None):
        """Actual method to read Redis settings from app configuration and initialize the StrictRedis instance.

        Positional arguments:
        app -- Flask application instance.
        config_prefix -- Prefix used in config key names in the Flask app's configuration. Useful for applications which
            interface with more than one Redis server. Default value is 'REDIS'. Will be converted to upper case (e.g.
            'REDIS_CACHE').
            Examples:
              REDIS_URL = 'redis://localhost/0'
              REDIS_CACHE_URL = 'redis://localhost/1'
        """
        # Normalize the prefix and add this instance to app.extensions.
        config_prefix = (config_prefix or 'REDIS').rstrip('_').upper()
        if not hasattr(app, 'extensions'):
            app.extensions = dict()
        if config_prefix.lower() in app.extensions:
            raise ValueError('Already registered config prefix {0!r}.'.format(config_prefix))
        app.extensions[config_prefix.lower()] = _RedisState(self, app)

        # Read config.
        args = read_config(app.config, config_prefix)

        # Instantiate StrictRedis.
        super(Redis, self).__init__(**args)  # Initialize fully.
