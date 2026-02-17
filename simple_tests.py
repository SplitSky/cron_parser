import pytest
from cron import CronSpec


def test_1():
    # check that cron generates the binary flips correctly
    cron = CronSpec("* * * * *")

    def simple_print(number: int):
        print(f"{bin(number)}, len={len(bin(number))-2}")

    items = [cron.minute, cron.hour, cron.day, cron.weekday, cron.month]
    for item in items:
        simple_print(item)


test_1()
