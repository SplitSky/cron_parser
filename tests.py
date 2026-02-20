from dataclasses import dataclass
from datetime import date
from types import ModuleType
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

def test_parsing_dow_overflow():
    cron = CronSpec("0 12 31 * 1")
    today = datetime(year=2026, month=2, day=20, hour=12, minute=0)
    correct_date = datetime(year=2026, month=2, day=23, hour=12, minute=0)
    dt_dow = find_dow(today, cron)
    assert dt_dow == correct_date

test_data = [
    ("* * * * *","2026-01-01T01:00:00"),
    ("5 4 * * 0","2026-02-22T04:05:00"), 
    ("0 0,12 1 */2 *", "2026-03-01T00:00:00"),
    ("0 4 8-14 * *", "2026-03-08T04:00:00"),
    ("0 0 1,15 * 3", "2026-02-25T00:00:00"),
    ("5 0 * 8 *", "2026-08-01T00:05:00"),
    ]

@pytest.mark.parametrize("cron,date", test_data)
def test_cron_matches(cron, date):
    cron = CronSpec(cron)
    dt = datetime.fromisoformat(date)
    assert cron.matches(dt)

# def test_find_day():
#     # tests both dow and dom cases and makes sure the correct date is chosen
#     # picks dow
#     cron = CronSpec("0 12 31 * 6") # At 12 on day of month 31 and on Sunday
#     print(cron.min)
#     print(cron.hr)
#     print(cron.dom)
#     print(cron.month)
#     print(cron.dow)
#     print("start expressions")
#     print(f"dow_star={cron.dow_star}")
#     print(f"dom_star={cron.dom_star}")
#     today = datetime(year=2026, month=2, day=20, hour=12, minute=0)
#     correct_date = datetime(year=2026, month=2, day=22, hour=12, minute=0)
#     dt = find_day(today, cron)
#     print(dt)
#     print(correct_date)

#def test_parsing_dow_not_overflow():
#    # the standard cron uses 0 - sunday. We use 0 - monday
#    cron = CronSpec("0 12 31 * 6")
#    print(cron.min)
#    print(cron.hr)
#    print(cron.dom)
#    print(cron.month)
#    print(cron.dow)
#    today = datetime(year=2026, month=2, day=20, hour=12, minute=0)
#    correct_date = datetime(year=2026, month=2, day=21, hour=12, minute=0)
#    dt_dow = find_dow(today, cron)
#    assert dt_dow == correct_date
