from collections.abc import Callable
import pytest
from syncloud.cli import create_parser, main_guts


@pytest.fixture
def parser():
    return create_parser('hello')


def test_parse_setup(parser):
    opts = parser.parse_args([
        'setup',
        '-b', 'test_bucket',
        '-q', 'test_queue',
    ])
    assert opts.command == 'setup'
    assert opts.bucket == 'test_bucket'
    assert opts.queue == 'test_queue'
    assert opts.template is not None
    assert isinstance(opts.func, Callable)


def test_parse_push(parser):
    opts = parser.parse_args([
        'push',
        '-b', 'test_bucket',
        '--path', '/tmp/abc',
    ])
    assert opts.command == 'push'
    assert opts.bucket == 'test_bucket'
    assert opts.path == '/tmp/abc'
    assert opts.prefix == ''
    assert opts.include is None
    assert opts.exclude is None
    assert isinstance(opts.func, Callable)


def test_parse_pull(parser):
    opts = parser.parse_args([
        'pull',
        '-b', 'test_bucket',
        '-q', 'test_queue',
        '--path', '/tmp/abc',
    ])
    assert opts.command == 'pull'
    assert opts.bucket == 'test_bucket'
    assert opts.queue == 'test_queue'
    assert opts.path == '/tmp/abc'
    assert opts.prefix == ''
    assert opts.include is None
    assert opts.exclude is None
    assert isinstance(opts.func, Callable)


def test_call_setup(mocker):
    m1 = mocker.patch(
        'syncloud.cli.create_stack',
        return_value=0)
    m2 = mocker.patch(
        'syncloud.cli.setup_bucket_notification',
        return_value=0)
    ret = main_guts([
        'syncloud', 'setup',
        '-b', 'test_bucket',
        '-q', 'test_queue',
    ])
    assert m1.call_count == 1
    assert m2.call_count == 1
    assert ret == 0
