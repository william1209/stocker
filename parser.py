from pandas_datareader import data  # pip install pandas_datareader
import matplotlib
#matplotlib.use('TkAgg')
import matplotlib.pyplot as plt    # pip install matplotlib
import pandas as pd                # pip install pandas
import time
import sys
import getopt



target=""

index=sys.argv[1]
if index=="twii":
    target="^TWII"
elif index=="dji":
    target="^DJI"
else:
    target=index+".TW"



kop=sys.argv[2]
if kop=="close":
    ktype="Close"
elif kop=="open":
    ktype="Open"
elif kop=="high":
    ktype="High"
elif kop=="low":
    ktype=="Low"

print ("fetching data for: "+target+" with "+kop+" type")






now=(time.strftime("%Y-%m-%d")) 

#print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 


data = data.DataReader(target, "yahoo", "2000-01-01", now)
c = data[ktype]
c.plot()
plt.show()




dit = {"price": c}
df = pd.DataFrame(dit)
df.to_csv("price.csv", columns=["price"])
