from cron import CronSpec
from datetime import datetime, timedelta
from typing import Set, Tuple, List
import copy
from calendar import monthrange


def max_days(year: int, month: int) -> int:
    return monthrange(year, month)[1]


def find_next(value: int, schedule: Set[int]) -> Tuple[bool, int]:
    # search for the value within the set and return the closest value higher than it
    new_mask = copy.deepcopy(schedule)  # has to deep copy
    new_mask.difference_update({x for x in schedule if x < value})
    # check if a value ahead exists
    if len(new_mask) == 0:
        return True, min(schedule)
    else:
        # find smallest value from new mask
        return False, min(new_mask)


def find_month(dt: datetime, cron: CronSpec, day_reset: bool = True) -> datetime:
    overflow, count = find_next(dt.month, cron.month)
    dt_out = dt
    if overflow:
        # increment year
        if day_reset:
            dt_out = dt_out.replace(
                year=dt.year + 1, month=count, day=1, hour=0, minute=0)
        else:
            dt_out = dt_out.replace(
                year=dt.year + 1, month=count, hour=0, minute=0)
    else:
        if count != dt_out.month:  # different month
            if day_reset:
                dt_out = dt_out.replace(month=count, day=1, hour=0, minute=0)
            else:
                dt_out = dt_out.replace(month=count, hour=0, minute=0)
        # else do nothing. Same month
    return dt_out


def find_dom(dt: datetime, cron: CronSpec) -> datetime:
    dt_return = dt
    overflow, count = find_next(dt.day, cron.dom)
    if overflow:
        # handle gracefully
        dt_return += timedelta(days=max_days(dt_return.year,
                               dt_return.month) - dt_return.day + count)
        # handle overflow in the month gracefully
        dt_return = find_month(dt_return, cron, False)
    else:
        # by definition of overflow count can't be less than dt.day
        dt_return += timedelta(days=count - dt.day)  # move by delta
        # check the month is still correct. Else set it

    dt_return = dt_return.replace(hour=0, minute=0)
    return dt_return


def find_dow(dt: datetime, cron: CronSpec) -> datetime:
    dt_return = dt
    fixed_weekday = (dt.weekday() + 1) % 7
    overflow, count = find_next(fixed_weekday, cron.dow)
    if overflow:
        delta = 7 - fixed_weekday + count
    else:
        delta = count - fixed_weekday
    if delta > 0:
        # TODO: experimental feature
        dt_return = dt_return.replace(hour=0, minute=0)
    dt_return += timedelta(days=delta)

    if not (dt_return.month in cron.month):  # check for month validity
        dt_return = find_month(dt_return, cron)

    return dt_return


def find_day(dt: datetime, cron: CronSpec) -> datetime:
    if cron.dom_star and cron.dow_star:
        return dt

    if not cron.dow_star and not cron.dom_star:
        dow_date = find_dow(dt, cron)
        dom_date = find_dom(dt, cron)
        return close_date_helper(dt, [dow_date, dom_date])

    if cron.dom_star:
        return find_dow(dt, cron)

    return find_dom(dt, cron)


def close_date_helper(today: datetime, dates: List[datetime]) -> datetime:
    closest = timedelta(days=1000000)
    chosen_date = None
    for date in dates:
        delta = date - today
        if delta >= timedelta(0) and delta < closest:
            chosen_date = date
            closest = delta
    if chosen_date is None:
        raise ValueError("The closest date not found")
    return chosen_date


def find_hour(dt: datetime, cron: CronSpec) -> datetime:
    overflow, count = find_next(dt.hour, cron.hr)
    if not overflow:
        if count != dt.hour:
            return dt.replace(hour=count, minute=0)
        return dt
    # overflow case
    dt_next_day = dt.replace(hour=0, minute=0) + timedelta(days=1)
    dt_next_day = find_day(dt_next_day, cron)
    first_valid_hour = min(cron.hr)
    return dt_next_day.replace(hour=first_valid_hour, minute=0)


def find_minute(dt: datetime, cron: CronSpec) -> datetime:
    overflow, count = find_next(dt.minute, cron.min)
    if not overflow:
        if count != dt.minute:
            return dt.replace(minute=count)
        return dt
    # overflow case
    dt_next_hour = dt.replace(minute=0) + timedelta(hours=1)
    dt_next_hour = find_hour(dt_next_hour, cron)
    first_valid_minute = min(cron.min)
    return dt_next_hour.replace(minute=first_valid_minute)


def find_next_schedule(cron: str, today: datetime) -> datetime:
    cron_spec = CronSpec(cron)
    dt = today.replace(second=0, microsecond=0)
    dt = find_month(dt, cron_spec)
    dt = find_day(dt, cron_spec)
    dt = find_hour(dt, cron_spec)
    dt = find_minute(dt, cron_spec)
    return dt
