from main import *

class Test():
    def test_1(self):
        cron = "* * * * *"
        cron_test = CronSpec(cron)
