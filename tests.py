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
    dt = find_month(today, cron, True)
    assert dt.month == 3

def test_parsing_dom():
    cron = CronSpec("0 12 6 2,7 *")
    today = datetime(year=2026, month=2, day=20, hour=0, minute=0)
    correct_date = datetime(year=2026, month=7, day=6, hour=0, minute=0)
    # NOTE: The hour is 0 because it is required to overflow and reset to 0
    dt_dom = find_dom(today, cron)
    assert dt_dom == correct_date

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


def test_find_day():
    cron = CronSpec("0 0 31 * 6")
    today = datetime(year=2026, month=2, day=22, hour=0, minute=0)
    dt = find_day(today, cron)
    correct_date = datetime(year=2026, month=2, day=28, hour=0, minute=0)
    assert correct_date == dt

def test_find_hour():
    cron = CronSpec("* 1 1 1 1")
    today = datetime(year=2026, month=2, day=22, hour=17, minute=0)
    correct_date = datetime(year=2027, month=1, day=1, hour=1, minute=0)
    dt = find_hour(today, cron)
    assert dt == correct_date

test_data = [
    ("5 4 * * 0","2026-03-01T04:05:00"),
    ("0 0,12 1 */2 *", "2026-03-01T00:00:00"),
    ("0 4 8-14 * *", "2026-03-08T04:00:00"), 
    ("0 0 1,15 * 3", "2026-02-25T00:00:00"),
    ("* * * * *","2026-02-22T17:47:00"),
    ("5 0 * 8 *", "2026-08-01T00:05:00"),
    ("5 0 * 1 *","2027-01-01T00:05:00")
    ]

@pytest.mark.parametrize("cron,date", test_data)
def test_find_next_date(cron, date):
    today = datetime.fromisoformat("2026-02-22T17:47:00")
    dt = find_next_schedule(cron, today)
    correct_date = datetime.fromisoformat(date)
    assert dt == correct_date
    
def find_next_date_edge_cases():
    # correct_date = datetime.fromisoformat("2026-02-20T18:30:00")
    cron, date = ("0 0 1,15 * 3", "2026-02-25T00:00:00")
    correct_date = datetime.fromisoformat(date)
    today = datetime.fromisoformat("2026-02-22T17:47:00")
    dt = find_next_schedule(cron, today)
    assert dt == correct_date

     # ("5 0 * 8 *", "2026-08-01T00:05:00"), # failing

def testing_final_case():
    cron, date = ("0 0 1,15 * 3", "2026-02-25T00:00:00")
    today = datetime.fromisoformat("2026-02-22T19:42:00")
    correct_date = datetime.fromisoformat(date)
    cron_spec = CronSpec(cron)
    dt = find_month(today, cron_spec)
    dt = find_day(dt, cron_spec)
    dt = find_hour(dt, cron_spec)
    dt = find_minute(dt, cron_spec)
    assert correct_date == dt

def test_1():
    cron, date_iso = ("5 4 * * 0","2026-03-01T04:05:00")
    correct_date = datetime.fromisoformat(date_iso) 
    today = datetime.fromisoformat("2026-02-22 20:34:16.731693")
    dt = find_next_schedule(cron, today)
    assert dt == correct_date
test_1()

big_test_data = [
("5 0 * 8 *","2026-08-01 00:05:00"),
("15 14 1 * *","2026-03-01 14:15:00"),
("0 22 * * 1-5","2026-02-23 22:00:00"),
#("23 0-20/2 * * *","2026-02-23 00:23:00"),
("0 0,12 1 */2 *","2026-03-01 00:00:00"),
("0 4 8-14 * *","2026-03-08 04:00:00"),
("5 0 * 8 *","2026-08-01 00:05:00"),
("15 14 1 * *","2026-03-01 14:15:00"),
("0 22 * * 1-5","2026-02-23 22:00:00"),
# ("23 0-20/2 * * *","2026-02-23 00:23:00"), # these test cases are not implemented on purpose
]

@pytest.mark.parametrize("cron,date", big_test_data)
def test_many_cases(cron, date):
    today = datetime.fromisoformat("2026-02-22T20:37:00")
    dt = find_next_schedule(cron, today)
    correct_date = datetime.fromisoformat(date)
    assert dt == correct_date


