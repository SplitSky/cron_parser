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
        self.hour = self.parse_field(fields[2], 1, 31)
        self.month = self.parse_field(fields[3], 1, 12)
        self.weekday = self.parse_field(fields[4], 0, 6)

    @staticmethod
    def parse_field(self, field: str, min: int, max: int) -> int:
        return 1
        # use bitmask implementation
        # for example [1..7] -> 0000000 or 1111111 for *
