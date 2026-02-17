from datetime import date, datetime, timedelta
from typing import Tuple


class DateMask:
    __slots__ = ("minute", "hour", "day", "month", "weekday", "date")

    def __init__(self, date_in: datetime):
        self.minute = 1 << date_in.minute
        self.hour = 1 << date_in.hour
        self.day = 1 << date_in.day
        self.month = 1 << date_in.month
        self.weekday = 1 << date_in.weekday()
        self.date = date_in

    def refresh(self):
        self.minute = 1 << self.minute
        self.hour = 1 << self.hour
        self.day = 1 << self.day
        self.month = 1 << self.month
        self.weekday = 1 << self.weekday()


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

    def count_zeroes(self, x: int):
        return (x & -x).bit_length() - 1

    def find_next_helper(self, schedule: int, target: int) -> Tuple[int, bool]:
        # this helper function takes in a schedule as bit mask and returns the index of the next available target
        if schedule == 0:
            raise ValueError("Schedule empty")
        k = self.count_zeroes(target)
        lower_mask = (1 << k) - 1
