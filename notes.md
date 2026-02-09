# Implementation Notes

1. Setup initial bitmask cron parser
2. Implement the silly OR logic for day of week/ day of month
3. Check that the datetime days 0-6 1-7 ranges are consistent



# Cron details
* all values
n single value
a-b range of values
*/n or a-b/s step
a,b,c list
no implementation on names
5 character cron
Like -> * * * * *

# The clever part
use bitmask to store complex checks and use bit shifts to quickly evalute
For example:
for minutes 0..59 becomes:
111111111111111111111111111111111111111111111111111111111111 -> (about 60)
Every minute allowed
Shift it left like (1 << 60) - 1
magic happens

# Extensions
1. Implement @yearly, @monthly, @daily -> Need to reason when servers
are actually available and working so may be stupid vanity


# Getting the next date from cron
The way to obtain the next date from the given cron is quite simple
Suppose you have a given date that has year, month, day, hour, minute
Then convert this date into a bit mask where one digit it set to 1 and the rest to 0
Then you assume that there will be a time at which the next run should happen

Then compare the two bit masks and see sequentially when the next one occurs
Today: 2017, 1 Jan, Monday, 12:00

Cron schedule gives you masks for year: mask-year, month: mask-month etc ...
Then you check:
```python
mask_year = Mask(Today.year)
# To see if they match exactly use (mask_year AND mask_year_cron)
```
To see if there is a day available descend into higher and higher resolution
1. Find next year available. Fix the year in return date
2. Find next month available. If overflow +1 to year. Fix the year and month in return date
3. Find next day available. If overflow +1 month. Fix the month, day in return date
4. etc for smaller and smaller increments

### How to find next date fast?
Both the date mask and the cron mask are binary numbers. What you are looking for is the closest digit that's 1
as compared to the date index.
First remove everything before index. Find closest significant digit to the date mask index.
This can be done by: (x & -x)
This does a cute bit flip and finds next bit
