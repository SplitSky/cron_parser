from typing import assert_never
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
    overflow, count = find_next(4, {1,2,7,8}, 1, 31)
    print(f"overflow={overflow}, count={count}")
    
    overflow, count = find_next(9, {1,2,7,8}, 1, 31)
    print(f"overflow={overflow}, count={count}")

test_find_next()

