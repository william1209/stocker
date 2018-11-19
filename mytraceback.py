from pandas_datareader import data  # pip install pandas_datareader
import matplotlib
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt    # pip install matplotlib
import pandas as pd                # pip install pandas

data = data.DataReader("^TWII", "yahoo", "2000-01-01", "2018-01-01")
c = data['Close']
c.plot()
plt.show()


c60mean = c.rolling(60, min_periods=1).mean()  # rolling60 means 取60天的範圍,
# min period means如果有NaN就跳過
# 60天最大值（c.rolling(60).max()）
# 60天平均（c.rolling(60).mean()）
# 60天最小值（c.rolling(60).min()）


# 畫圖
c['2015':].plot()
c60mean['2015':].plot()


# 買入訊號
# 假設買入訊號是收盤價大於60天均價
signal = (c > c60)

# 回測並跟大盤比較
(c.shift(-1) / c)[signal].cumprod().plot(color='red')
(c.shift(-1) / c).cumprod().plot(color='blue')

# shift(-1)代表右移＝隔天的收盤價
# (c.shift(-1) / c)代表成長率
# (c.shift(-1) / c)[signal]意思是指取signal為true的時候來計算成長率
# cumprod()是將成長率全部成起來，如果大於一資產是成長的，小於一資產打折
