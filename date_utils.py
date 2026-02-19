from cron import CronSpec
from datetime import date, datetime, timedelta
from typing import Set, Tuple

def find_month(dt: datetime, cron: CronSpec) -> datetime:
    overflow, count = find_next(dt.month, cron.month)
    dt_out = dt
    if overflow:
        # increment year
        dt_out = dt_out.replace(year=dt.year + 1)
    dt_out = dt_out.replace(month=count)
    return dt_out

# def find_day(dt: datetime, ):


def next_date(today: datetime, cron: CronSpec) -> datetime:
    dt = today.replace(second=0, microsecond=0)
    dt += timedelta(minutes=1) # strictly after now
    # find month
    overflow, count = find_next(dt.month, cron.month)
    print(overflow)
    print(count)

    return dt

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
