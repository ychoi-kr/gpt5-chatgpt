def radian(x):
    return x / 180 * 3.1415

for x in range(0, 360, 90):
    print('度: {}, ラジアン: {:.2f}'.format(x, radian(x)))