from datetime import datetime
from meteostat import Point, Daily

from influxdb import influxdb_post
from ArimaModel import Forecast

import matplotlib.pyplot as plt
import pandas as pd

class Meteo:
	def __init__(self,measurement):
		self.lat = None
		self.long = None
		self.start = None
		self.start = None
		self.location = None
		self.data = None
		self.measurement=measurement

	def get_coord(self):
		print("gps default: Bologna")
		self.lat, self.long=44.497612, 11.353733

	def set_time(self,start,end):
		self.start=datetime(start[0],start[1],start[2])
		self.end=datetime(end[0],end[1],end[2])

	def set_location(self,height=70):
		self.get_coord()
		self.location =  Point(self.lat, self.long, height)

	def get_interval_meteo(self,start,end):
		self.set_time(start,end)
		self.set_location()
		data = Daily(self.location, self.start, self.end)
		self.data = data.fetch()

	def plot_data(self):
		try:
			self.data.plot(y=['tavg', 'tmin', 'tmax'])
			plt.show()
		except:
			print("[PLOT DATA] no data to visualize")

	def get_data_raw(self):
		tavg = self.data.to_dict()["tavg"]
		new_data_list = [] 
		for k, v in tavg.items():
			new_data_list.append({"Time":k,"GPS":[self.lat, self.long],"Temperature":v})

		return new_data_list

	def build_dataframe(self,start,end,measurement=None):
		if measurement is not None:
			self.measurement=measurement
		self.get_interval_meteo(start,end)
		return self.get_data_raw()

	def post_data_raw(self, measurement=None):
		if measurement is not None:
			self.measurement=measurement

		lista=self.get_data_raw()
		influxdb_post(pd.DataFrame(lista), measurement=self.measurement, tag_col=["GPS"])

class MeteoPredictor(Meteo):
	@staticmethod
	def meteo2pd(df):
		df1 =df.copy()
		df1 = pd.DataFrame({ "y": df})
		df1.reset_index(inplace=True)
		df1 = df1.rename(columns = {'time':'ds'})
		return df1

	@staticmethod
	def pd2series(df,name_series="y"):
		df1=df.copy()
		df1= df1.set_index('ds')
		df1.index.name="ds"
		return df1.squeeze().rename(name_series)

	@staticmethod
	def series2pd(df):
		df=df.to_frame()
		df.reset_index(inplace=True)
		df=df.rename(columns={"ds":"Time","Meteostat_Temperature_predicted":"Temperature_predicted"})
		return df

	@staticmethod
	def series2pd_indexed(df):
		df=df.to_frame()

		return df	

	def get_data_pred(self):
		tavg = MeteoPredictor.series2pd_indexed(self.predictions).to_dict()["Meteostat_Temperature_predicted"]
		new_data_list = [] 

		for k, v in tavg.items():
			new_data_list.append({"Time":k,"GPS":[self.lat, self.long],"Temperature_predicted":v})
		return new_data_list

	def predict(self,n_periods=365):
		df =self.data.tavg.dropna()
		df_pd = MeteoPredictor.meteo2pd(df)
		df = MeteoPredictor.pd2series(df_pd,"Meteostat"+"_Temperature")

		forcast=Forecast(df)
		forcast.tuning()
		forcast.fit(df.name)
		self.predictions=forcast.forecast(df.name,n_periods)
		# forcast.plot_forecast() #####IMPORTANTE
		self.predictions.index.name="ds"
		
		return self.predictions

	def post_data_pred(self,measurement=None):
		if measurement is not None:
			self.measurement=measurement
		lista=self.get_data_pred()
		
		post_df = pd.DataFrame(lista)
		post_df["Temperature_predicted"] = post_df["Temperature_predicted"].apply(lambda x: round(x,1))
		influxdb_post(post_df, measurement=self.measurement,tag_col=["GPS"])

if __name__ == '__main__':
	meteor = MeteoPredictor(measurement="meteostat-FinalTest")
	meteor.build_dataframe(start=(2020, 12, 1),end=(2022, 7, 1))
	meteor.post_data_raw()
	meteor.predict()
	meteor.post_data_pred()


	

