import pandas as pd
import numpy as np
#from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.arima.model import ARIMA
from meteo import Meteo
from matplotlib import pyplot as plt

start, end = (2022, 1, 1), (2022, 7, 1)
meteor=Meteo()
meteor.get_interval_meteo(start,end)
#meteor.plot_data()



df =meteor.data.tavg.dropna()
df.index = pd.to_datetime(df.index)
df_shape =df.shape[0]
df =df.squeeze()
#print(df)

import matplotlib.pyplot as plt
import seaborn; 
seaborn.set()
#df.plot();



## 1,1,2 ARIMA Model
#model = ARIMA(df, order=(1,1,1))
#model_fit = model.fit()
#print(model_fit.summary())

#residuals = pd.DataFrame(model_fit.resid)
#fig, ax = plt.subplots(1,2)
#residuals.plot(title="Residuals", ax=ax[0])
#residuals.plot(kind='kde', title='Density', ax=ax[1])
#plt.show()




idx =pd.RangeIndex(start=df_shape, stop=df_shape+20)
idx

# Build Model
# model = ARIMA(train, order=(3,2,1))  
model2 = ARIMA(df ,order=(2, 1, 1))  
fitted = model2.fit()  

# Forecast
#print(fitted.forecast(50, alpha=0.05))
fc = fitted.forecast(20, alpha=0.05)  # 95% conf
fc2 = fitted.get_forecast(20, alpha=0.05)
conf=fc2.conf_int( alpha=0.05)
#print(conf)


# Make as pandas series
date= pd.date_range('2022-07-02', '2022-07-21', freq='D') 
date= pd.Series(date)
fc_series = pd.Series(fc)#, index=date)
#fc_series.reset_index(inplace=True)



dftest = pd.Series(list(fc_series), index=date)
#pd.DataFrame({"time": date, "tavg": list(fc_series)})
#print(dftest)


dft=pd.concat([df, dftest])


lower_series= pd.Series(list(np.array(conf)[:,0]), index=date)
upper_series= pd.Series(list(np.array(conf)[:,1]), index=date)
#lower_series = pd.Series(conf[:, 0], index=idx)
#upper_series = pd.Series(conf[:, 1], index=idx)

# Plot
plt.figure(figsize=(12,5), dpi=100)
plt.xlim(pd.Timestamp('2022-06-01'),pd.Timestamp('2022-07-21'))

plt.plot(df, label='training')
plt.plot(dftest, label='forecast')
plt.fill_between(lower_series.index, lower_series, upper_series, 
                 color='r', alpha=.15)
plt.title('Forecast vs Actuals')
plt.legend(loc='upper left', fontsize=8)
plt.show()

  
