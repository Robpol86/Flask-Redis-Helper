from flask.ext.redis import read_config


def test_url():
    config = dict(REDIS_URL='redis://localhost')
    expected = dict(host='localhost')
    actual = read_config(config, 'REDIS')
    assert expected == actual


def test_socket():
    config = dict(REDIS_URL='redis+socket:///tmp/file.sock')
    expected = dict(unix_socket_path='/tmp/file.sock')
    actual = read_config(config, 'REDIS')
    assert expected == actual

    config = dict(REDIS_SOCKET='/tmp/file.sock')
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

    config = dict(REDIS_URL='redis+socket:///tmp/file.sock', REDIS_DB=3)
    expected = dict(unix_socket_path='/tmp/file.sock', db=3)
    actual = read_config(config, 'REDIS')
    assert expected == actual

    config = dict(REDIS_SOCKET='/tmp/file.sock', REDIS_DB=3)
    actual = read_config(config, 'REDIS')
    assert expected == actual


def test_prefix():
    config = dict(REDIS_SOCKET='/tmp/file.sock', REDIS_DB=3, REDIS2_SOCKET='/tmp/file.sock', REDIS2_DB=1,
                  REDIS3_URL='redis://localhost', REDIS3_PASSWORD='P@ssWord')

    expected = dict(unix_socket_path='/tmp/file.sock', db=3)
    actual = read_config(config, 'REDIS')
    assert expected == actual

    expected = dict(unix_socket_path='/tmp/file.sock', db=1)
    actual = read_config(config, 'REDIS2')
    assert expected == actual

    expected = dict(host='localhost', password='P@ssWord')
    actual = read_config(config, 'REDIS3')
    assert expected == actual
