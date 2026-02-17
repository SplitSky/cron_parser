def b(x: int):
    print(f"{x} = {bin(x)}")


# x = 1 << 5
# b(x)
# y = (1 << 3) | (1 << 5) | (1 << 26)
# b(y)
# z = x & -x
# b(z)

def count_zeroes(x: int):
    return (x & -x).bit_length() - 1


schedule = 0
for i in range(0, 6, 1):
    schedule |= 1 << i

today = 1 << 2
print("today`")
b(today)

k = count_zeroes(today)
print(f"k = {k}")
lower_mask = (1 << k) - 1
print("lower mask")
b(lower_mask)
print("future mask")
future_mask = mask & ~lower_mask
b(future_mask)
