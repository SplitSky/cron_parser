from datetime import datetime
from typing import Iterable, Tuple, Union, Optional


class CronExp:
    __slots__ = ("minute", "hour", "dom", "month",
                 "dow", "dow_rest", "dom_rest")

    def __init__(self, expression: str):
        fields = expression.split()
        if len(fields) != 5:
            raise ValueError(
                "Cron expressions must have 5 fields. Wrong format")

        self.dow_rest = True
        self.dom_rest = True

        if fields[4] == "*":  # set type of cron
            self.dow_rest = False

        if fields[2] == "*":
            self.dom_rest = False

        self.minute = self.parse_field(fields[0], 0, 59)
        self.hour = self.parse_field(fields[1], 0, 23)
        self.dom = self.parse_field(fields[2], 1, 31)
        self.month = self.parse_field(fields[3], 1, 12)
        self.dow = self.parse_field(fields[4], 0, 6)  # 0=Sun

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

    def matches(self, dt: datetime) -> bool:
        # lil bit of modulus to fix the range issue
        cron_weekday = (dt.weekday() + 1) % 7
        return bool((self.minute >> dt.minute) & 1 and (self.hour >> dt.hour) & 1 and (self.dom >> dt.day) & 1 and (self.month >> dt.month) & 1 and (self.dow >> cron_weekday) & 1)
