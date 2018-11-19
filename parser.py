from pandas_datareader import data  # pip install pandas_datareader
import matplotlib
#matplotlib.use('TkAgg')
import matplotlib.pyplot as plt    # pip install matplotlib
import pandas as pd                # pip install pandas
import time

now=(time.strftime("%Y-%m-%d")) 

#print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 


data = data.DataReader("^TWII", "yahoo", "2000-01-01", now)
c = data['Close']
c.plot()
plt.show()


dit = {"price": c}

df = pd.DataFrame(dit)

df.to_csv("price.csv", columns=["price"])
