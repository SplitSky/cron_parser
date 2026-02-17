from datetime import datetime, timedelta
from typing import Iterable, Tuple, Union, Optional


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
        self.date = today
        self.date = self.date.replace(second=0, microsecond=0)
        self.refresh_masks()

        print(self.date)
        items = [self.minute, self.hour, self.day,
                 self.month, self.weekday]
        names = ["minutes", "hours", "days", "months", "weekday"]
        for name, item in zip(names, items):
            self.fun_print(item, name)

    def refresh_masks(self):
        self.minute = self.parse_date(int(self.date.minute))
        self.hour = self.parse_date(int(self.date.hour))
        self.day = self.parse_date(int(self.date.day))
        self.month = self.parse_date(int(self.date.month))
        self.weekday = self.parse_date(int(self.date.weekday()))

    def parse_date(self, field: int) -> int:
        return 1 << field

    def fun_print(self, number: int, name: str):
        print(f"name={name}, bin = {bin(number)}, zeroes = {
              self.count_zeroes(number)}")

    def count_zeroes(self, x: int) -> int:
        # use 2s complement to get the index of least significant bit
        return (x & -x).bit_length() - 1

    def next_index(self, schedule: int, today: int) -> Tuple[int, bool]:
        if schedule == 0:
            # return None, False
            raise ValueError("The cron schedule is 0")
        k = self.count_zeroes(today)
        lower_mask = (1 << k) - 1
        future_mask = schedule & ~lower_mask

        if future_mask != 0:
            # some day exists
            return self.count_zeroes(future_mask), False
        return self.count_zeroes(schedule), True  # overflow

    def find_nearest(self, cron: CronSpec):
        # cron is dow or dom
        # cron type
        cron_type = cron.dow
        dt = self.date

        while True:
            # find month
            count, overflow = self.next_index(
                cron.month, self.parse_date(dt.month))
            if overflow:
                dt = dt.replace(year=dt.year+1)
                dt = dt.replace(month=0, day=0, hour=0,
                                minute=0, second=0, microsecond=0)
            dt = dt.replace(month=count)
            print(f"first={dt}")

            while True:
                # DOW
                if cron_type:  # Day of week to be used
                    print(f"week check={dt}")
                    # find_weekday
                    count, overflow = self.next_index(
                        cron.weekday, self.parse_date(dt.weekday()))
                    # count contains number of days to go forward. if overflow + 7
                    delta = count - self.date.weekday()
                    if overflow:
                        delta += 7 - dt.weekday()
                        dt = dt + timedelta(days=delta)
                        break
                    dt = dt + timedelta(days=delta)
                    # back to find month
                else:
                    # find day
                    print(f"day check={dt}")
                    count, overflow = self.next_index(
                        cron.day, self.parse_date(dt.day))
                    if overflow:
                        dt = dt.replace(month=dt.month+1)
                        dt = dt.replace(day=0, hour=0, minute=0,
                                        second=0, microsecond=0)
                        break  # return to check month
                    dt = dt.replace(day=count)
                    # back to find month
                # DOW end

                while True:
                    # find hour
                    print(f"hour check={dt}")
                    count, overflow = self.next_index(
                        cron.hour, self.parse_date(dt.hour))
                    if overflow:
                        dt += timedelta(days=1)  # see if next day also matches
                        # back to DOW
                        break
                    dt = dt.replace(hour=count)

                    # find minute

                    print(f"minute check={dt}")
                    count, overflow = self.next_index(
                        cron.minute, self.parse_date(dt.minute))
                    if overflow:
                        dt += timedelta(hours=1)
                        # back to hour
                    else:
                        dt = dt.replace(minute=count)
                        return dt
