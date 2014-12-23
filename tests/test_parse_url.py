import os

from flask_redis import parse_url

import pytest

TMP_DIR = 'C:/Windows/Temp' if os.name == 'nt' else '/tmp'


def test_bad_urls():
    """Make sure bad URLs raise ValueError."""
    urls = [None, [1, 2, 3], 'efesfesf', '://localhost', 'http://google.com', '{0}/dne/redis.sock'.format(TMP_DIR),
            'redis://localhost/test', 'file://localhost/0', 'redis+socket://username:password@localhost:6379/0']
    for url in urls:
        with pytest.raises(ValueError):
            parse_url(url)


def test_socket_paths():
    """Test various socket paths work."""
    actual = parse_url('file://user:pass@redis.sock')
    assert dict(password='pass', unix_socket_path='redis.sock') == actual

    actual = parse_url('file://user:pass@{0}/redis.SOCK'.format(TMP_DIR))
    assert dict(password='pass', unix_socket_path='{0}/redis.SOCK'.format(TMP_DIR)) == actual

    actual = parse_url('file://user:pass@../redis.sock')
    assert dict(password='pass', unix_socket_path='../redis.sock') == actual

    actual = parse_url('file://user:pass@./redis.sock')
    assert dict(password='pass', unix_socket_path='./redis.sock') == actual

    actual = parse_url('file://redis.SOCK')
    assert dict(unix_socket_path='redis.SOCK') == actual

    actual = parse_url('file://{0}/redis.sock'.format(TMP_DIR))
    assert dict(unix_socket_path='{0}/redis.sock'.format(TMP_DIR)) == actual

    actual = parse_url('file://../redis.sock')
    assert dict(unix_socket_path='../redis.sock') == actual

    actual = parse_url('file://./redis.SOCK')
    assert dict(unix_socket_path='./redis.SOCK') == actual

    # Duplicate tests for redis+socket:// scheme.
    actual = parse_url('redis+socket://user:pass@redis.sock')
    assert dict(password='pass', unix_socket_path='redis.sock') == actual

    actual = parse_url('redis+socket://user:pass@{0}/redis.SOCK'.format(TMP_DIR))
    assert dict(password='pass', unix_socket_path='{0}/redis.SOCK'.format(TMP_DIR)) == actual

    actual = parse_url('redis+socket://user:pass@../redis.sock')
    assert dict(password='pass', unix_socket_path='../redis.sock') == actual

    actual = parse_url('redis+socket://user:pass@./redis.sock')
    assert dict(password='pass', unix_socket_path='./redis.sock') == actual

    actual = parse_url('redis+socket://redis.SOCK')
    assert dict(unix_socket_path='redis.SOCK') == actual

    actual = parse_url('redis+socket://{0}/redis.sock'.format(TMP_DIR))
    assert dict(unix_socket_path='{0}/redis.sock'.format(TMP_DIR)) == actual

    actual = parse_url('redis+socket://../redis.sock')
    assert dict(unix_socket_path='../redis.sock') == actual

    actual = parse_url('redis+socket://./redis.SOCK')
    assert dict(unix_socket_path='./redis.SOCK') == actual

    # Test implicit.
    actual = parse_url('redis://user:pass@{0}/redis.SOCK'.format(TMP_DIR))
    assert dict(password='pass', unix_socket_path='{0}/redis.SOCK'.format(TMP_DIR)) == actual

    actual = parse_url('redis://user:pass@../redis.sock')
    assert dict(password='pass', unix_socket_path='../redis.sock') == actual

    actual = parse_url('redis://user:pass@./redis.sock')
    assert dict(password='pass', unix_socket_path='./redis.sock') == actual

    actual = parse_url('redis://{0}/redis.sock'.format(TMP_DIR))
    assert dict(unix_socket_path='{0}/redis.sock'.format(TMP_DIR)) == actual

    actual = parse_url('redis://../redis.sock')
    assert dict(unix_socket_path='../redis.sock') == actual

    actual = parse_url('redis://./redis.SOCK')
    assert dict(unix_socket_path='./redis.SOCK') == actual


def test_network_urls():
    """Test various non-socket URLs."""
    actual = parse_url('redis://user:pass@localhost:6379/1')
    assert dict(password='pass', host='localhost', port=6379, db=1) == actual

    actual = parse_url('redis://192.168.1.100:8000/1')
    assert dict(host='192.168.1.100', port=8000, db=1) == actual

    actual = parse_url('redis://redis.myserver.com:8000')
    assert dict(host='redis.myserver.com', port=8000) == actual

    actual = parse_url('redis://user:pass@localhost')
    assert dict(password='pass', host='localhost') == actual

    actual = parse_url('redis://localhost/2')
    assert dict(host='localhost', db=2) == actual

    actual = parse_url('redis://localhost/')
    assert dict(host='localhost') == actual

    actual = parse_url('redis://localhost')
    assert dict(host='localhost') == actual
