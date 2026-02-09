from datetime import datetime
from typing import Iterable

class CronSpec:
    __slots__ = ("minute", "hour", "day", "month", "weekday")

    def __init__(self, expression: str):
        fields = expression.split()
        if len(fields) != 5:
            raise ValueError("Cron expressions must have 5 fields. Wrong format")
        self.minute = self.parse_field(fields[0],0,59)
        self.hour = self.parse_field(fields[1], 0, 23)
        self.day = self.parse_field(fields[2], 1, 31)
        self.month = self.parse_field(fields[3], 1, 12)
        self.weekday = self.parse_field(fields[4], 0, 6)

    def matches(self, dt: datetime) -> bool:
        cron_weekday = (dt.weekday() + 1) % 7 # lil bit of modulus to fix the range issue
        return bool((self.minute >> dt.minute) & 1 and (self.hour >> dt.hour) & 1 and (self.day >> dt.day) & 1 and (self.month >> dt.month) & 1 and (self.weekday >> cron_weekday) & 1)
    
    def parse_field(self, field: str, min: int, max: int) -> int:
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

class CronDate:

    __slots__ = ("minute", "hour", "day", "month", "weekday", "date")

    def __init__(self, today: datetime):
        # set details given the date
        self.minute = self.parse_date(int(today.minute))
        self.hour = self.parse_date(int(today.hour))
        self.day = self.parse_date(int(today.day))
        self.month = self.parse_date(int(today.month))
        self.weekday = self.parse_date(int(today.weekday()))
        self.date = today

    def parse_date(self, field: int) -> int:
        return 1 << field

    def next_date(self, cron: CronSpec) -> datetime:
        date_out = self.date
        year = date_out.year
        # find next year



        return date_out
        




