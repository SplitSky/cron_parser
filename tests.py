from dataclasses import dataclass
from datetime import date
from typing import assert_never
from _pytest.config import ConftestImportFailure
from _pytest.monkeypatch import monkeypatch
import pytest
from cron import CronSpec
from date_utils import *

def test_parsing_star():
    cron = CronSpec("* * * * *")
    assert min(cron.min) == 0
    assert max(cron.min) == 59
    assert min(cron.hr) == 0
    assert max(cron.hr) == 23
    assert min(cron.dom) == 1
    assert max(cron.dom) == 31
    assert min(cron.month) == 1
    assert max(cron.month) == 12
    assert min(cron.dow) == 0
    assert max(cron.dow) == 6

def test_parsing_range():
    cron = CronSpec("* * * * 1-3")
    assert {1, 2, 3} == cron.dow
    cron = CronSpec("* * * * 1-6")
    assert {1, 2, 3, 4, 5 ,6} == cron.dow

def test_parsing_coma():
    cron = CronSpec("* * * * 1,2,3,4")
    assert {1, 2, 3, 4} == cron.dow

def test_parsing_coma_and_range():
    cron = CronSpec("* * * * 1,3-4")
    assert {1, 3, 4} == cron.dow

def test_step():
    cron = CronSpec("*/15 * * * *")
    assert {0, 15, 30, 45} == cron.min
    
def test_step_with_start():
    cron = CronSpec("15/15 * * * *")
    assert {15, 30, 45} == cron.min

def test_find_next():
    overflow, count = find_next(4, {1,2,7,8})
    assert overflow == False
    assert count == 7
    overflow, count = find_next(9, {1,2,7,8})
    assert overflow == True
    assert count == 1

def test_find_month():
    today = datetime(year=2020, month=1, day=1, hour=12, minute=0)
    cron = CronSpec("* * * 3 *")
    dt = find_month(today, cron)
    assert dt.month == 3

def test_parsing_dom():
    cron = CronSpec("0 12 6 2,7 *")
    today = datetime(year=2026, month=2, day=20, hour=12, minute=0)
    correct_date = datetime(year=2026, month=7, day=6, hour=12, minute=0)
    dt_dom = find_dom(today, cron)
    assert dt_dom == correct_date

def test_parsing_dow():
    cron = CronSpec("0 12 * 7 2")
    today = datetime(year=2026, month=2, day=20, hour=12, minute=0)
    correct_date = datetime(year=2026, month=7, day=7, hour=12, minute=0)

    dt_dow = find_dow(today, cron)
    print(dt_dow)

def test_find_day():
    today = datetime.today()
    cron = CronSpec("0 12 6 * *")
    closest_date = datetime(minute=0, hour=12, day=6, month=3, year=2026)
    dt_dow = find_dow(today, cron)
    dt_dom = find_dom(today, cron)
    dt = find_day(today, cron)
    print(f"dow = {dt_dow}")
    print(f"dom = {dt_dom}")
    print(f"dt = {dt}")
    print(f"correct = {closest_date}")


# test_find_day()
test_parsing_dow()
