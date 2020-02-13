import logging

from syncloud.utils import logger, log_result


def test_log_result(caplog):
    logger.setLevel(logging.DEBUG)
    log_result('testing', '123')
    assert len(caplog.records) == 2
    assert caplog.records[0].levelno == logging.INFO
    assert caplog.records[0].message == 'testing'
    assert caplog.records[1].levelno == logging.DEBUG
    assert caplog.records[1].message == '123'
