from importlib import import_module


def test_import_utils():
    mod = import_module('syncloud.utils')
    dirmod = dir(mod)
    assert 'logger' in dirmod
    assert 'log_result' in dirmod
    assert 'get_queue_details' in dirmod


def test_import_setup():
    mod = import_module('syncloud.setup')
    dirmod = dir(mod)
    assert 'create_stack' in dirmod
    assert 'setup_bucket_notification' in dirmod


def test_import_cli():
    mod = import_module('syncloud.cli')
    dirmod = dir(mod)
    assert 'create_parser' in dirmod
    assert 'main' in dirmod
    assert 'main_guts' in dirmod
