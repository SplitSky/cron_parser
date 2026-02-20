from cron import CronSpec
from datetime import datetime, timedelta
from typing import Set, Tuple, List
import copy

def find_next(value: int,schedule: Set[int]) -> Tuple[bool, int]:
    # search for the value within the set and return the closest value higher than it
    new_mask = copy.deepcopy(schedule) # has to deep copy
    new_mask.difference_update({x for x in schedule if x < value})
    print(new_mask)
    print(new_mask)
    # check if a value ahead exists
    if len(new_mask) == 0:
        return True, min(schedule)
    else:
        # find smallest value from new mask
        return False, min(new_mask)

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
        dt_return = dt_return.replace(month= dt_return.month + 1, day=count) # overflow to next month
        # re-check month
        dt_return = find_month(dt_return, cron)
    else:
        # by definition of overflow count can't be less than dt.day
        dt_return += timedelta(days=count - dt.day) # move by delta
        dt_return = find_month(dt_return, cron)

    return dt_return

def find_dow(dt: datetime, cron: CronSpec) -> datetime:
    dt_return = dt
    overflow, count = find_next(dt.weekday(), cron.dow)
    print(f"overflow = {overflow}")
    print(f"count = {count}")
    if overflow:
        print("overflow branch")
        delta = 6 - dt.weekday() + count
    else:
        print("not overflow branch")
        delta = count - dt.weekday()
    dt_return += timedelta(days=delta)
    dt_return = find_month(dt_return, cron) # check for month overflow
    return dt_return

def find_day(dt: datetime, cron: CronSpec) -> datetime:
    if not cron.dow_star and not cron.dom_star:
        # OR logic finding closest
        dow_date = find_dow(dt, cron)
        dom_date = find_dom(dt, cron)
        print(f"dow_date = {dow_date}")
        print(f"dom_date = {dom_date}")
        return close_date_helper(dt, [dow_date, dom_date])
    elif cron.dom_star and not cron.dow_star:
        return find_dow(dt, cron)
    else:
        print(f"dom_date = {find_dom(dt, cron)}")
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

    print(f"closest date is = {closest}")

    if chosen_date is None:
        raise ValueError("The closest date not found")
    return chosen_date

def find_hour(dt: datetime, cron: CronSpec) -> datetime:
    overflow, count = find_next(dt.hour, cron.hr)
    if overflow:
        dt_return = dt + timedelta(hours=23-dt.hour+count)
        dt_return = find_day(dt_return, cron)
    else:
        dt_return = dt + timedelta(hours=count - dt.hour)
        dt_return = find_day(dt_return, cron)

    return dt_return

def find_minute(dt: datetime, cron: CronSpec) -> datetime:
    overflow, count = find_next(dt.minute, cron.min)
    if overflow:
        dt_return =  dt + timedelta(minutes=59 - dt.minute + count)
        dt_return = find_hour(dt_return, cron)
    else:
        dt_return = dt + timedelta(minutes=count + dt.minute)
        dt_return = find_hour(dt_return, cron)

    return dt_return


