def b(x: int):
    print(f"{x} = {bin(x)}")


x = 1 << 5
b(x)
y = (1 << 3) | (1 << 5) | (1 << 26)
b(y)
z = x & -x
b(z)
