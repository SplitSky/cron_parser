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

