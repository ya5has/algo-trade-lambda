price = float("402.6")
target = float("398.574")
stoploss = float("407.626")
squareoff = round((target - price), 1)
stoploss = round((price - stoploss), 1)

print(squareoff, stoploss)
