import os

from flask.ext.redis import read_config

SOCK_FILE_PATH = 'C:\\Windows\\Temp\\file.sock' if os.name == 'nt' else '/tmp/file.sock'


def test_url():
    config = dict(REDIS_URL='redis://localhost')
    expected = dict(host='localhost')
    actual = read_config(config, 'REDIS')
    assert expected == actual


def test_socket():
    config = dict(REDIS_URL='redis+socket://{0}'.format(SOCK_FILE_PATH))
    expected = dict(unix_socket_path=SOCK_FILE_PATH)
    actual = read_config(config, 'REDIS')
    assert expected == actual

    config = dict(REDIS_SOCKET=SOCK_FILE_PATH)
    actual = read_config(config, 'REDIS')
    assert expected == actual


def test_piecemeal():
    config = dict(REDIS_HOST='localhost', REDIS_PORT=9999, REDIS_DB=2)
    expected = dict(host='localhost', port=9999, db=2)
    actual = read_config(config, 'REDIS')
    assert expected == actual


def test_hybrid():
    config = dict(REDIS_URL='redis://localhost', REDIS_PORT=9999)
    expected = dict(host='localhost', port=9999)
    actual = read_config(config, 'REDIS')
    assert expected == actual

    config = dict(REDIS_URL='redis+socket://{0}'.format(SOCK_FILE_PATH), REDIS_DB=3)
    expected = dict(unix_socket_path=SOCK_FILE_PATH, db=3)
    actual = read_config(config, 'REDIS')
    assert expected == actual

    config = dict(REDIS_SOCKET=SOCK_FILE_PATH, REDIS_DB=3)
    actual = read_config(config, 'REDIS')
    assert expected == actual


def test_prefix():
    config = dict(REDIS_SOCKET=SOCK_FILE_PATH, REDIS_DB=3,
                  REDIS2_SOCKET=SOCK_FILE_PATH, REDIS2_DB=1, REDIS3_URL='redis://localhost',
                  REDIS3_PASSWORD='P@ssWord')

    expected = dict(unix_socket_path=SOCK_FILE_PATH, db=3)
    actual = read_config(config, 'REDIS')
    assert expected == actual

    expected = dict(unix_socket_path=SOCK_FILE_PATH, db=1)
    actual = read_config(config, 'REDIS2')
    assert expected == actual

    expected = dict(host='localhost', password='P@ssWord')
    actual = read_config(config, 'REDIS3')
    assert expected == actual
