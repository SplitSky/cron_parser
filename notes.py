number = 0
bin_number = bin(number)

def super_print(number: int):
    print(number)
    print(str(bin(number))[2:])

# setting a number on a mask
# 1. Set all to on
number = (1 << 60) - 1
super_print(number)

# 2. reset and set a range on
number = 0
for shift in range(10, 21):
    number |= 1 << shift
super_print(number)

# 3. reset and set single digits
number = 0
for shift in [1,12,23]:
    number |= 1 << shift
super_print(number)
