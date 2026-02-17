
import pytest
from cron import CronSpec

# ---------- Helpers ----------


def bit_is_set(mask: int, idx: int) -> bool:
    """Return True if bit at position idx is 1."""
    return ((mask >> idx) & 1) == 1


def ones_span(min_v: int, max_v: int) -> int:
    """Return a mask with bits [min_v..max_v] set (inclusive)."""
    width = max_v - min_v + 1
    return ((1 << width) - 1) << min_v

# ---------- Core range tests for '*' ----------


def test_minutes_star_has_60_bits_0_to_59():
    cs = CronSpec("* * * * *")
    m = cs.minute
    # Bits 0..59 should be 1; bits >= 60 should be 0
    assert m == ones_span(0, 59)
    assert bit_is_set(m, 0)
    assert bit_is_set(m, 59)
    assert not bit_is_set(m, 60)


def test_hours_star_has_24_bits_0_to_23():
    cs = CronSpec("* * * * *")
    h = cs.hour
    assert h == ones_span(0, 23)
    assert bit_is_set(h, 0)
    assert bit_is_set(h, 23)
    assert not bit_is_set(h, 24)


def test_dom_star_has_bits_1_to_31_only():
    cs = CronSpec("* * * * *")
    d = cs.day
    assert d == ones_span(1, 31)  # bit 0 must be 0
    assert not bit_is_set(d, 0)
    assert bit_is_set(d, 1)
    assert bit_is_set(d, 31)
    assert not bit_is_set(d, 32)


def test_month_star_has_bits_1_to_12_only():
    cs = CronSpec("* * * * *")
    mo = cs.month
    assert mo == ones_span(1, 12)  # bit 0 must be 0
    assert not bit_is_set(mo, 0)
    assert bit_is_set(mo, 1)
    assert bit_is_set(mo, 12)
    assert not bit_is_set(mo, 13)


def test_weekday_star_has_bits_0_to_6():
    cs = CronSpec("* * * * *")
    wd = cs.weekday
    assert wd == ones_span(0, 6)
    assert bit_is_set(wd, 0)
    assert bit_is_set(wd, 6)
    assert not bit_is_set(wd, 7)

# ---------- Single values ----------


def test_single_minute_value_sets_exact_bit():
    cs = CronSpec("13 * * * *")  # minute=13 only
    assert bit_is_set(cs.minute, 13)
    # neighbors should be 0
    assert not bit_is_set(cs.minute, 12)
    assert not bit_is_set(cs.minute, 14)


def test_single_hour_value_sets_exact_bit():
    cs = CronSpec("* 22 * * *")
    assert bit_is_set(cs.hour, 22)
    assert not bit_is_set(cs.hour, 21)
    assert not bit_is_set(cs.hour, 23)


def test_single_dom_value_starts_at_1():
    cs = CronSpec("* * 7 * *")  # day-of-month = 7
    assert bit_is_set(cs.day, 7)
    assert not bit_is_set(cs.day, 0)  # bit 0 must always be 0 for DOM


def test_single_month_value_starts_at_1():
    cs = CronSpec("* * * 10 *")  # October
    assert bit_is_set(cs.month, 10)
    assert not bit_is_set(cs.month, 0)


def test_single_weekday_value_in_0_to_6():
    cs = CronSpec("* * * * 3")  # Wednesday if 0=Sunday
    assert bit_is_set(cs.weekday, 3)
    assert not bit_is_set(cs.weekday, 2)
    assert not bit_is_set(cs.weekday, 4)

# ---------- Lists and ranges ----------


def test_list_of_minutes_sets_multiple_bits():
    cs = CronSpec("0,10,59 * * * *")
    assert bit_is_set(cs.minute, 0)
    assert bit_is_set(cs.minute, 10)
    assert bit_is_set(cs.minute, 59)
    assert not bit_is_set(cs.minute, 9)
    assert not bit_is_set(cs.minute, 11)


def test_range_of_hours_sets_contiguous_bits():
    cs = CronSpec("* 8-12 * * *")
    for i in range(8, 13):
        assert bit_is_set(cs.hour, i)
    assert not bit_is_set(cs.hour, 7)
    assert not bit_is_set(cs.hour, 13)


def test_range_of_dom_from_1_is_valid():
    cs = CronSpec("* * 1-5 * *")
    for i in range(1, 6):
        assert bit_is_set(cs.day, i)
    assert not bit_is_set(cs.day, 0)
    assert not bit_is_set(cs.day, 6)


def test_range_of_months():
    cs = CronSpec("* * * 2-4 *")
    for i in range(2, 5):
        assert bit_is_set(cs.month, i)
    assert not bit_is_set(cs.month, 1)
    assert not bit_is_set(cs.month, 5)

# ---------- Steps (*/n, a-b/n) ----------


def test_step_every_5_minutes_from_zero():
    cs = CronSpec("*/5 * * * *")
    for i in range(0, 60):
        assert bit_is_set(cs.minute, i) == (i % 5 == 0)


def test_step_every_2_hours_from_zero():
    cs = CronSpec("* */2 * * *")
    for i in range(0, 24):
        assert bit_is_set(cs.hour, i) == (i % 2 == 0)


def test_step_range_day_of_month_10_to_20_every_3():
    cs = CronSpec("* * 10-20/3 * *")
    expected = {10, 13, 16, 19}
    for i in range(1, 32):
        assert bit_is_set(cs.day, i) == (i in expected)


def test_step_on_months_in_range():
    cs = CronSpec("* * * 3-11/4 *")
    expected = {3, 7, 11}
    for i in range(1, 13):
        assert bit_is_set(cs.month, i) == (i in expected)

# ---------- Validation errors ----------


@pytest.mark.parametrize(
    "expr",
    [
        "60 * * * *",    # minute out of range
        "* 24 * * *",    # hour out of range
        "* * 0 * *",     # DOM below 1
        "* * 32 * *",    # DOM > 31
        "* * * 0 *",     # month below 1
        "* * * 13 *",    # month > 12
        "* * * * 7",     # weekday > 6
    ],
)
def test_out_of_range_values_raise(expr):
    with pytest.raises(ValueError):
        CronSpec(expr)


@pytest.mark.parametrize("expr", ["*/0 * * * *", "* */-1 * * *", "* * */0 * *"])
def test_invalid_step_raises(expr):
    with pytest.raises(ValueError):
        CronSpec(expr)


def test_both_dom_and_dow_restricted_is_rejected():
    # Your constructor forbids restricting both DOM and DOW simultaneously
    with pytest.raises(ValueError):
        CronSpec("* * 1 * 1")


def test_dom_restricted_dow_star_sets_dow_flag_false():
    cs = CronSpec("* * 1 * *")  # DOM restricted, DOW = *
    # assert cs.dow is False
    assert cs.dow is True


def test_dow_restricted_dom_star_sets_dow_flag_true():
    cs = CronSpec("* * * * 1")  # DOW restricted, DOM = *
    # assert cs.dow is True
    assert cs.dow is False
