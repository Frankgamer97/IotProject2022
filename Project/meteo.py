from datetime import datetime, timezone
import matplotlib.pyplot as plt
from meteostat import Point, Daily
from utility import listvalues
import pandas as pd
from influxdb import influxdb_post, get_dataframe_from_influxdb
from arima_model import Forecast, get_predictions_list


			

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
		if len(listvalues) > 0:
			self.lat =listvalues[0]["GPS"][0]
			self.long=listvalues[0]["GPS"][1]		
		else:
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
			print("no data to visualize")


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
		'''
		table=pd.DataFrame(self.get_data_raw())
		dte=pd.to_datetime(table["Time"])
		print(dte)
		print(table)
		#print()
		dta=pd.date_range("2020-12-1","2022-07-1",freq="D")
		print(dta)
		#print("hey")
		#dte = pd.to_datetime(dte,dayfirst=True)
		#print("hoy")
		#print(dte)
		table["Time"]=dta
		print(table)
		#table=table.set_index('Time')
		'''
		#for el in lista:
		influxdb_post(pd.DataFrame(lista), measurement=self.measurement, tag_col=["GPS"])

	'''
	def post_meteo(self, start, end,measurement=None):
		if measurement is not None:
			self.measurement=measurement
		self.get_interval_meteo(start,end)
		self.post_data_raw()
	'''


'''
	def get_meteo(self):
	        return get_dataframe_from_influxdb(self.measurement,name="Meteostat_")

	def get_pred_list(self,series_list):
	        return get_predictions_list(series_list)


	def get_predicted_meteostat(self):
	        series_list=self.get_meteo()

	        prediction_list=self.get_pred_list(series_list)


	        df_gps={}
	        for df in list_series:
	                if "GPS" in df.name:
	                      df_gps=df


	        df_gps_predictions=pd.Series(list(df_gps), index=prediction_list[0].index).rename(df_gps.name+"_predicted")

	        df_total=pd.concat([df_gps_predictions,prediction_list[0]],axis=1)
	        print("--------------------------------------------------->")
	        df_total.reset_index(inplace=True)
	        df_total = df_total.rename(columns = {'index':'Time'})
	        self.meteo_predicted=df_total
	        return df_total

	def post_predictions(self):
	        for i in range(self.meteo_predicted.shape[0]):
	                #print(dict(self.meteo_predicted.iloc[i]))
	                influxdb_post(pd.DataFrame(dict(self.meteo_predicted.iloc[i])), type_data="forecasted_meteostat", measurement=self.measurement)
	        
'''


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
			#print(k,v)

		return new_data_list



	def predict(self,n_periods=365):
		#start, end = (2020, 12, 1), (2022, 7, 1)
		#meteor=Meteo(measurement="testFinal2-meteostat")
		#meteor.get_interval_meteo(start,end)
		##meteor.plot_data()

		df =self.data.tavg.dropna()

		df_pd = MeteoPredictor.meteo2pd(df)
		df = MeteoPredictor.pd2series(df_pd,"Meteostat"+"_Temperature")

		# print(df)
		# print(type(df))

		forcast=Forecast(df)
		forcast.tuning()
		forcast.fit(df.name)
		self.predictions=forcast.forecast(df.name,n_periods)
		# forcast.plot_forecast()

		self.predictions.index.name="ds"
		# print(self.predictions)
		return self.predictions

	def post_data_pred(self,measurement=None):
		if measurement is not None:
			self.measurement=measurement
		lista=self.get_data_pred()
		influxdb_post(pd.DataFrame(lista), measurement=self.measurement,tag_col=["GPS"])





def main_meteostat_backup():
	        start, end = (2020, 12, 1), (2022, 7, 1)
	        meteor=Meteo(measurement="testFinal2-meteostat")
	        meteor.get_interval_meteo(start,end)
	        #meteor.plot_data()

	        df =meteor.data.tavg.dropna()
	        #df.index = pd.to_datetime(df.index)
	        #df_shape =df.shape[0]
	        #df =df.squeeze()
	        df_pd = meteo2pd(df)
	        df = pd2series(df_pd,"meteostat"+"_Temperature")

	        print(df)
	        print(type(df))

	        forcast=Forecast(df)
	        #print("SEASON",forcast.D)
	        #print("STATION",forcast.d)
	        forcast.tuning()
	        forcast.fit(df.name)
	      
	        predictions=forcast.forecast(df.name,Forecast.seasonality)
	        # forcast.plot_forecast()
	        predictions.index.name="ds"
	        return predictions


if __name__ == '__main__':
	
	#meteor = Meteo()
	#meteor.get_interval_meteo((2022, 7, 1),(2022, 7, 16))
	# lista=meteor.get_data_raw()
	#meteor.post_data_raw(measurement="test1-meteostat")

#	meteor =Meteo(measurement="testFinal3-meteostat")
	#meteor.get_interval_meteo((2020, 12, 1), (2022, 7, 1))
	#table=pd.DataFrame(meteor.get_data_raw())
	#table=table.set_index('Time')
	#print(table)

#	meteor.post_meteo( (2020, 12, 1), (2022, 7, 1))


	#series_list=meteor.get_meteo()
	#for df in series_list:
#		print(df)
	#meteor.get_predicted_meteostat()
	#meteor.post_predictions()

	meteor = MeteoPredictor(measurement="testFinal5-meteostat")
	meteor.build_dataframe(start=(2020, 12, 1),end=(2022, 7, 1))
	meteor.post_data_raw()
	meteor.predict()
	meteor.post_data_pred()


	

'''
	predictions=main_meteostat()
	predictions=predictions.to_frame()
	predictions.reset_index(inplace=True)
	predictions=predictions.rename(columns={"ds":"Time","meteostat_Temperature_predictions":"Temperature_predicted"})#meteostat_Temperature_predictions
	#influxdb_post(predictions, type_data="meteostat_predicted", measurement=self.measurement,single_point=False,tag_columns=["GPS"],field_columns =["Temperature_predicted"])
	
	print(predictions)
	print(type(predictions))
'''

