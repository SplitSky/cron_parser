from datetime import date, datetime, timedelta
from cron_parser import CronExp
from typing import Tuple, dataclass_transform


def count_zeroes(x: int):
    return (x & -x).bit_length() - 1


def next_index(schedule: int, today: int, dow: bool) -> Tuple[int, bool]:
    if dow:
        today = (today + 1) % 7
    if schedule == 0:
        # return None, False
        raise ValueError("The cron schedule is 0")
    k = count_zeroes(today)
    lower_mask = (1 << k) - 1
    future_mask = schedule & ~lower_mask

    if future_mask != 0:
        # some day exists
        return count_zeroes(future_mask), False
    return count_zeroes(schedule), True  # overflow


def increment_month(dt: datetime) -> datetime:
    # increment the month by 1
    dt_out = dt + timedelta(days=31)
    dt_out = dt_out.replace(day=dt.day)
    return dt_out


def find_month(dt: datetime, cron_mask: int) -> datetime:
    count, overflow = next_index(cron_mask, dt.month, False)
    if overflow:
        return dt.replace(year=dt.year + 1, month=count)
    return dt.replace(month=count)


def find_day(dt: datetime, cron: CronExp) -> datetime:
    # if dow restricted
    # find next date using dom
    count, overflow = next_index(cron.dom, dt.day, False)
    if overflow:
        # month overflow
        dt_dom = increment_month(dt)
    dt_dom = dt + timedelta(days=count)

    count, overflow = next_index(cron.dow, dt.weekday(), True)
    # c = count
    # t = today day in weekday
    t = (dt.weekday() + 1) % 7

    if overflow:
        dt_dow = dt + timedelta(days=(7 - t + count))
    else:
        dt_dow = dt + timedelta(days=(count - t))

    # compare which is nearest
    delta1 = abs((dt - dt_dom).seconds)
    delta2 = abs((dt - dt_dow).seconds)
    if delta1 < delta2:
        return dt_dom
    else:
        return dt_dow


def find_hour(dt: datetime, cron: CronExp) -> datetime:
    dt_out = dt
    count, overflow = next_index(cron.hour, dt.hour, False)
    if overflow:
        dt_out += timedelta(days=1)
    dt_out += timedelta(hours=count)
    return dt_out


def find_minute(dt: datetime, cron: CronExp) -> datetime:
    dt_out = dt
    count, overflow = next_index(cron.minute, dt.minute, False)
    if overflow:
        dt_out += timedelta(hours=1)
    dt_out += timedelta(minutes=count)
    return dt_out


def next_date(today: datetime, cron: CronExp) -> datetime:
    MAX_ITER = 100
    for i in range(0, MAX_ITER):
        dt = find_month(today, cron.month)
        dt = find_day(dt, cron)
        dt = find_hour(dt, cron)
        dt = find_minute(dt, cron)

        if cron.matches(dt):
            return dt
        else:
            print(f"Iteration number: {i}")
