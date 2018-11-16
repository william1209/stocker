from pandas_datareader import data  # pip install pandas_datareader
import matplotlib
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt    # pip install matplotlib
import pandas as pd                # pip install pandas

data = data.DataReader("^TWII", "yahoo", "2000-01-01", "2018-01-01")
c = data['Close']
c.plot()
plt.show()


dit = {"price": c}

df = pd.DataFrame(dit)

df.to_csv("price.csv", columns=["price"])
