# Implementation Notes

1. Setup initial bitmask cron parser
2. Implement the silly OR logic for day of week/ day of month
3. Check that the datetime days 0-6 1-7 ranges are consistent
4.


# Cron details
* all values
n single value
a-b range of values
*/n or a-b/s step
a,b,c list
no implementation on names
5 character cron
Like -> * * * * *


# Extensions
1. Implement @yearly, @monthly, @daily -> Need to reason when servers
are actually available and working so may be stupid vanity

