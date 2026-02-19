from datetime import datetime
from types import LambdaType
from typing import Set

# special cron characters substitutions
SPECIALS = {
        "@yearly": "0 0 1 1 *",
        "@monthly": "0 0 1 * *",
        "@weekly": "0 0 * * 0",
        "@daily": "0 0 * * *",
        "@hourly": "0 * * * *"
        }

"""convention for ranges
minutes: 0 - 59
hours: 0 - 23
day: 1 - 31
month: 1 - 12
year: 1900 - 9999
dow: 0 - 6 (6 == Sunday)
"""

class CronSpec:
    def __init__(self, cron_expr: str):
        parts = cron_expr.split()
        if len(parts) > 5:
            raise ValueError("Cron length exceeded")

        if cron_expr in SPECIALS.keys(): # substitution for specials
            parts = SPECIALS[cron_expr].split()

        self.dom_star = False
        if parts[2] == "*":
            self.dom_star = True

        self.dow_star = False
        if parts[4] == "*":
            self.dow_star = True

        self.min = set(self.parse_expression(parts[0], 0, 59))
        self.hr = set(self.parse_expression(parts[1], 0, 23))
        self.dom = set(self.parse_expression(parts[2], 1, 31))
        self.month = set(self.parse_expression(parts[3], 1, 12))
        self.dow = set(self.parse_expression(parts[4], 0, 6))

    def parse_expression(self, expr: str, min: int, max: int) -> Set[int]:
        # specials , - * /
        return_set = set()

        if expr == "*":
            return set(range(min, max+1, 1))

        if "," in expr:
            # list of allowed values may include ranges
            parts = expr.split(",")
            for part in parts:
                if "-" in part:
                    temp = part.split("-")
                    return_set.update(set(range(int(temp[0]), int(temp[1])+1,1)))
                else:
                    return_set.add(int(part))
        
        if "/" in expr:
            parts = expr.split("/")
            if "*/" in expr:
                step = int(expr.split("/")[1])
                return_set.update(set(range(min, max+1, step)))
            else:
                start, step = expr.split("/")
                return_set.update(set(range(int(start), max, int(step))))

        if "-" in expr and "," not in expr:
            # simple range
            parts = expr.split("-")
            return_set.update(set(range(int(parts[0]), int(parts[1])+1, 1)))
        
        # if single number
        if expr.isdigit():
            return_set.add(int(expr))

        return return_set


