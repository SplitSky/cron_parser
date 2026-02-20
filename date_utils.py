from cron import CronSpec
from datetime import datetime, timedelta
from typing import Set, Tuple, List

def find_month(dt: datetime, cron: CronSpec) -> datetime:
    overflow, count = find_next(dt.month, cron.month)
    dt_out = dt
    if overflow:
        # increment year
        dt_out = dt_out.replace(year=dt.year + 1)
    dt_out = dt_out.replace(month=count)
    return dt_out

def find_dom(dt: datetime, cron: CronSpec) -> datetime:
    dt_return = dt
    overflow, count = find_next(dt.day, cron.dom)
    if overflow:
        dt_return = dt_return.replace(month= dt_return.month + 1, day=1) # overflow to next month
        dt_return += timedelta(days=count) # push to next available day
    else:
        # by definition of overflow count can't be less than dt.day
        dt_return += timedelta(days=count - dt.day) # move by delta

    return dt_return

def find_dow(dt: datetime, cron: CronSpec) -> datetime:
    dt_return = dt
    overflow, count = find_next(dt.weekday(), cron.dow)
    if overflow:
        delta = 7 - dt.weekday() + count
    else:
        delta = count - dt.weekday()
    dt_return += timedelta(days=delta)

    return dt_return

def find_day(dt: datetime, cron: CronSpec) -> datetime:
    if cron.dow_star and cron.dom_star:
        # OR logic finding closest
        dow_date = find_dow(dt, cron)
        dom_date = find_dom(dt, cron)
        return close_date_helper(dt, [dow_date, dom_date])
    elif cron.dom_star and not cron.dow_star:
        return find_dow(dt, cron)
    else:
        return find_dom(dt, cron)

def next_date(today: datetime, cron: CronSpec) -> datetime:
    dt = today.replace(second=0, microsecond=0)
    dt += timedelta(minutes=1) # strictly after now
    # find month
    overflow, count = find_next(dt.month, cron.month)
    print(overflow)
    print(count)
    return dt

def close_date_helper(today: datetime, dates: List[datetime]) -> datetime:
    closest = timedelta(days=1000000)
    chosen_date = None
    for date in dates:
        delta = abs(today - date)
        if delta < closest:
            chosen_date = date
            closest = delta

    if chosen_date is None:
        raise ValueError("The closest date not found")
    return chosen_date

def find_hour(dt: datetime, cron: CronSpec) -> datetime:
    overflow, count = find_next(dt.hour, cron.hr)
    if overflow:
        return dt + timedelta(hours=23-dt.hour+count)
    else:
        return dt + timedelta(hours=count - dt.hour)

def find_minute(dt: datetime, cron: CronSpec) -> datetime:
    overflow, count = find_next(dt.minute, cron.min)
    if overflow:
        return dt + timedelta(minutes=59 - dt.minute + count)
    else:
        return dt + timedelta(minutes=count + dt.minute)

def find_next(value: int,schedule: Set[int]) -> Tuple[bool, int]:
    # search for the value within the set and return the closest value higher than it
    new_mask = schedule.copy() # has to deep copy
    new_mask.difference_update({x for x in schedule if x < value})
    print("new mask")
    print(new_mask)
    # check if a value ahead exists
    if len(new_mask) == 0:
        return True, min(schedule)
    else:
        # find smallest value from new mask
        return False, min(new_mask)
