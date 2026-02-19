from datetime import datetime
import pytest

from cron_parser import CronExp   # adjust import path if needed
from date_util import *


def test_1():
    cron = CronExp("* * * * *")
    assert cron.matches(datetime(2026, 1, 1, 0, 0))


def test_2():
    # exact match
    cron = CronExp("0 12 17 6 3")
    assert cron.matches(datetime(2026, 6, 17, 12, 0))  # 2026-June-17 12:00


@pytest.mark.parametrize(
    "dt,expected",
    [
        (datetime(2026, 1, 1, 10, 0), True),
        (datetime(2026, 1, 1, 10, 59), True),
        (datetime(2026, 1, 1, 11, 0), False),
    ],
)
def test_3(dt, expected):
    # minute one
    cron = CronExp("* 10 * * *")
    assert cron.matches(dt) is expected


@pytest.mark.parametrize(
    "minute,expected",
    [
        (0, True),
        (15, True),
        (30, True),
        (45, True),
        (14, False),
    ],
)
def test_4(minute, expected):
    # step minutes
    cron = CronExp("*/15 * * * *")
    dt = datetime(2026, 1, 1, 0, minute)
    assert cron.matches(dt) is expected


@pytest.mark.parametrize(
    "minute,expected",
    [
        (10, True),
        (15, True),
        (20, True),
        (12, False),
    ],
)
def test_5(minute, expected):
    # step minutes
    cron = CronExp("10-20/5 * * * *")
    dt = datetime(2026, 1, 1, 0, minute)
    assert cron.matches(dt) is expected


def test_6():
    # test hour range
    cron = CronExp("0 9-17 * * *")
    assert cron.matches(datetime(2026, 1, 1, 9, 0))
    assert cron.matches(datetime(2026, 1, 1, 17, 0))
    assert not cron.matches(datetime(2026, 1, 1, 18, 0))


@pytest.mark.parametrize(
    "minute,expected",
    [
        (5, True),
        (10, True),
        (55, True),
        (6, False),
    ],
)
def test_7(minute, expected):
    # minutes list
    cron = CronExp("5,10,55 * * * *")
    dt = datetime(2026, 1, 1, 0, minute)
    assert cron.matches(dt) is expected


def test_8():
    # cluster fuck with ranges
    cron = CronExp("0,30 9-17 * * *")
    assert cron.matches(datetime(2026, 1, 1, 9, 0))
    assert cron.matches(datetime(2026, 1, 1, 10, 30))
    assert not cron.matches(datetime(2026, 1, 1, 10, 15))


def test_9():
    cron = CronExp("0 0 1 * *")
    assert cron.matches(datetime(2026, 2, 1, 0, 0))
    assert not cron.matches(datetime(2026, 2, 2, 0, 0))


def test_10():
    cron = CronExp("0 0 * 12 *")
    assert cron.matches(datetime(2026, 12, 1, 0, 0))
    assert not cron.matches(datetime(2026, 11, 1, 0, 0))


def test_11():
    cron = CronExp("0 0 * * 0")  # Sunday
    assert cron.matches(datetime(2026, 2, 8, 0, 0))   # Sunday
    assert not cron.matches(datetime(2026, 1, 5, 0, 0))  # Monday


@pytest.mark.parametrize(
    "expr",
    [
        "* * * *",
        "61 * * * *",
        "* 24 * * *",
        "*/0 * * * *",
        "10-5 * * * *",
    ],
)
def test_invalid(expr):
    with pytest.raises(ValueError):
        CronExp(expr)


def test_12():
    # text next date features
    date_now = datetime(year=2026, month=2, day=19, hour=6, minute=1)
    date_correct = datetime(year=2026, month=2, day=19, hour=12, minute=0)
    cron = CronExp("0 12 * * *")
    date_predicted = next_date(date_now, cron)
    print(date_predicted)
    print(date_now)


test_12()
