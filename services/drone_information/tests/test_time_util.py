import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import time_util


@pytest.fixture(scope="module")
def epoch_time():
    yield 1517481030#01 Feb 2018, 10:30:30


def test_epoch_to_datetime(epoch_time):
    assert time_util.epoch_to_datetime(epoch_time) == '01 Feb 2018, 10:30:30'


def test_epoch_to_datetime_with_dashes(epoch_time):
    assert time_util.epoch_to_datetime_with_dashes(epoch_time) == '2018-02-01 10:30:30'


def test_epoch_to_time(epoch_time):
    assert time_util.epoch_to_time(epoch_time) == '10:30:30'


if __name__ == '__main__':
    pytest.main()