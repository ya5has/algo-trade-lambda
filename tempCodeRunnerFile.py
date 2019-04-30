price = float("552.15")
target = float("557.6715")
stoploss = float("546.6285")
squareoff = round((target - price), 1)
stoploss = round((price - stoploss), 1)

print(stoploss, squareoff, price)