from stocker import Stocker as stk
import pandas as pd
#price = pd.read_csv('price.csv')  

df = pd.read_csv('price.csv', index_col='Date', parse_dates=['Date'])
price = df.squeeze()
price.head()

#print(df)
target = stk(price)

#twii.changepoint_prior_analysis(changepoint_priors=[0.001, 0.05, 0.1, 0.2]) 
#比較各個prior間誤差並plot

target.changepoint_prior_scale = 0.5 #change prior scale
target.predict_future(days=10)
