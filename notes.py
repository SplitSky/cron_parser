

def super_print(number: int):
    print(f"number = {number} - {bin(number)}")
    # print(f"binary = {str(bin(number))[2:]}")


def ctz(x: int) -> int:
    return (x & -x).bit_length() - 1


def next_allowed_date(A: int, B: int, n_bits: int) -> int:
    if A <= 0 or (A & (A - 1)) != 0:
        raise ValueError("A must have exactly one bit set (power of two).")

    if n_bits <= 0:
        raise ValueError("n_bits must be positive.")

    max_bit = n_bits
    mask_high = (1 << (max_bit + 1)) - 1
    if A & ~mask_high:
        raise ValueError("A is outside the allowed n_bits range (offset=1).")
    B &= mask_high

    i = ctz(A)

    # Include today: clear bits [0..i-1]
    if i == 0:
        lower_mask = 0
    else:
        lower_mask = (1 << i) - 1
    future = B & ~lower_mask

    if future == 0:
        raise ValueError("Overflow")

    next_index = ctz(future & -future)
    day = next_index  # offset=1
    if not (1 <= day <= n_bits):
        raise ValueError("out of bounds")
    return int(day)


def main():
    number = 0
    bin_number = bin(number)
    # setting a number on a mask
    # 1. Set all to on
    number = (1 << 60) - 1
    # super_print(number)

    # 2. reset and set a range on
    number = 0
    for shift in range(10, 21):
        number |= 1 << shift
    # super_print(number)

    # 3. reset and set single digits
    number = 0
    for shift in [1, 12, 23]:
        number |= 1 << shift
    # super_print(number)

    number = 0
    for shift in [1, 5, 12, 23]:
        number |= 1 << shift
    # super_print(number)
    d = 5
    d_mask = 1 << d
    # super_print(d_mask)

    number1 = 21
    super_print(number1)
    number2 = bin(number1)
    number2 = -number2
    number2 = int(number2)
    super_print(number2)
    number3 = ~number1
    result = number1 & -number1


main()
