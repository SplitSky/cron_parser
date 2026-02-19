from cron import CronSpec
from datetime import datetime, timedelta
from typing import Set, Tuple

def is_year_leap(year: int) -> bool:
    if year % 4 == 0:
        return True

    if year % 100 == 0:
        if year % 400 == 0:
            return True
        
    return False

def max_month_days(month: int, year: int) -> int:
    if month == 2:
        if is_year_leap(year):
            return 29
        else:
            return 28
    else:
        if month in [4, 6, 9, 11]:
            return 30
        else:
            return 31


def next_date(today: datetime, cron: CronSpec) -> datetime:
    dt = today.replace(second=0, microsecond=0)
    dt += timedelta(minutes=1) # strictly after now
    # find month
    overflow, count = find_next(dt.month, cron.month,1 ,max_month_days(dt.month, dt.year))
    print(overflow)
    print(count)

    return dt

def find_next(value: int,schedule: Set[int], min_range: int, max_range: int) -> Tuple[bool, int]:
    # search for the value within the set and return the closest value higher than it
    new_mask = schedule.copy()
    new_mask.difference_update({x for x in schedule if x < value})
    # check if a value ahead exists
    if len(new_mask) == 0:
        return True, min(schedule)
    else:
        # find smallest value from new mask
        return False, min(new_mask)
