from datetime import date, datetime, timedelta
from typing import Tuple, Callable, Dict, Any


class DateMask:
    __slots__ = ("minute", "hour", "day", "month", "weekday", "date")

    def __init__(self, date_in: datetime):
        self.minute = 1 << date_in.minute
        self.hour = 1 << date_in.hour
        self.day = 1 << date_in.day
        self.month = 1 << date_in.month
        self.weekday = 1 << ((date_in.weekday() + 1) % 7)
        self.date = date_in

    def refresh(self, date_in):
        self.minute = 1 << date_in.minute
        self.hour = 1 << date_in.hour
        self.day = 1 << date_in.day
        self.month = 1 << date_in.month
        self.weekday = 1 << ((date_in.weekday() + 1) % 7)
        self.date = date_in


class CronSpec:
    __slots__ = ("minute", "hour", "day", "month", "weekday", "dow")

    def __init__(self, expression: str):
        fields = expression.split()
        if len(fields) != 5:
            raise ValueError(
                "Cron expressions must have 5 fields. Wrong format")

        if fields[4] != "*" and fields[2] != "*":
            raise ValueError(
                "Cron is incorrect. Contains restruction on weekday and month day")

        if fields[4] == "*":  # set type of cron
            self.dow = True
        elif fields[2] == "*":
            self.dow = False
        else:
            raise ValueError(
                "Incorrect cron. Day and week field can't both be restricted")

        self.minute = self.parse_field(fields[0], 0, 59)
        self.hour = self.parse_field(fields[1], 0, 23)
        self.day = self.parse_field(fields[2], 1, 31)
        self.month = self.parse_field(fields[3], 1, 12)
        self.weekday = self.parse_field(fields[4], 0, 6)

    def matches(self, dt: datetime) -> bool:
        # lil bit of modulus to fix the range issue
        cron_weekday = (dt.weekday() + 1) % 7
        return bool((self.minute >> dt.minute) & 1 and (self.hour >> dt.hour) & 1 and (self.day >> dt.day) & 1 and (self.month >> dt.month) & 1 and (self.weekday >> cron_weekday) & 1)

    def parse_field(self, field: str, min: int, max: int) -> int:
        # doesn't handle OR logic. Just raises exception on init
        mask = 0
        for part in field.split(","):
            if part == "*":
                return ((1 << (max - min + 1)) - 1) << min

            step = 1
            if "/" in part:
                part, step_str = part.split("/")
                step = int(step_str)
                if step <= 0:
                    raise ValueError("Step must be pos")

            if part == "*":
                start, end = min, max
            elif "-" in part:
                start_str, end_str = part.split("-")
                start, end = int(start_str), int(end_str)
            else:
                start = end = int(part)

            if start < min or end > max or start > end:
                raise ValueError("Value out of range")

            for v in range(start, end + 1, step):
                mask |= 1 << v

        return mask


def count_zeroes(x: int):
    return (x & -x).bit_length() - 1


def is_leap_year(year: int) -> bool:
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    return year % 4 == 0


def max_days_in_month(year, month) -> int:
    if month == 2:
        return 29 if is_leap_year(year) else 28
    if month in (4, 6, 9, 11):
        return 30
    return 31


def adjust_days_range(date: datetime, schedule: int) -> int:
    # TODO: check indexes are correct
    # fixes the schedule to make sure not allowed
    # day values are excluded from schedule
    md = max_days_in_month(date.year, date.month)
    valid = ((1 << md) - 1) << 1
    return schedule & valid


def find_next_helper(schedule: int, target: int) -> Tuple[int, bool]:
    # this helper function takes in a schedule as bit mask and
    # returns the index of the next available target
    if schedule == 0:
        raise ValueError("Schedule empty")
    k = count_zeroes(target)
    lower_mask = (1 << k) - 1
    future_mask = schedule & ~lower_mask
    if future_mask != 0:
        return count_zeroes(future_mask), False
    return count_zeroes(schedule), True  # overflow return nearest


def find_next_date(cron: CronSpec, date_start: datetime):
    # returns a date for the next cron scheduled date
    # convert date into mask
    a = 1


def find_month(cron: CronSpec, target: DateMask) -> DateMask:
    count, overflow = find_next_helper(cron.month, target.month)
    dt = target.date
    if overflow:
        # increment year
        dt = target.date.replace(year=target.date.year + 1)

    if dt.month == 12:
        # edge case for overflow
        # reset back to January
        dt = target.date.replace(year=target.date.year + 1, month=1)
    else:
        dt = dt.replace(month=dt.month+1)

    return_mask = target
    return_mask.refresh(dt)
    return return_mask


def find_day(cron: CronSpec, target: DateMask):
    dt = target.date
    if cron.dow:
        # only day of the week
        count, overflow = find_next_helper(cron.weekday, target.weekday)
        if overflow:
            # increment the date and see if it overflows the month
            delta = 6 - dt.day + count  # TODO: Verify the index works
            new_date = dt + timedelta(days=delta)
            # check if next month
            if new_date.month > dt.month:
                # increment

    else:
        # only day of the month


def find_hour(cron: CronSpec, hour: int, dt: datetime):
    a = 1


def find_minute(cron: CronSpec, minute: int, dt: datetime):
    a = 1
