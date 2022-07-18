from datetime import datetime, timezone
import matplotlib.pyplot as plt
from meteostat import Point, Daily
from utility import listvalues
import pandas as pd
from influxdb import influxdb_post




class Meteo:
	def __init__(self):
		self.lat = None
		self.long = None
		self.start = None
		self.start = None
		self.location = None
		self.data = None

	def get_coord(self):
		if len(listvalues) > 0:
			self.lat =listvalues[0]["GPS"][0]
			self.long=listvalues[0]["GPS"][1]		
		else:
			print("gps default: Bologna")
			self.lat, self.long=44.497612, 11.353733
			

	def set_time(self,start,end):
		self.start=datetime(start[0],start[1],start[2])
		self.end=datetime(end[0],end[1],end[2],end[3],end[4])

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


	def get_data(self):
		tavg = self.data.to_dict()["tavg"]
		new_data_list = [] 
		for k, v in tavg.items():
			new_data_list.append({"Time":k,"Temperature":v,"GPS":[self.lat, self.long]})

		return new_data_list


	def post_data(self,measurement="test1-meteostat"):
		lista=self.get_data()
		for el in lista:
			influxdb_post(el, type_data="meteostat", measurement=measurement)

	def post_meteo(self, start, end,measurement="test1-meteostat"):
		self.get_interval_meteo(start,end)
		self.post_data(measurement)
	

if __name__ == '__main__':
	#meteor = Meteo()
	#meteor.get_interval_meteo((2022, 7, 1),(2022, 7, 16))
	# lista=meteor.get_data()
	#meteor.post_data(measurement="test1-meteostat")
	
	Meteo().post_meteo( (2022, 7, 1), (2022, 7, 31, 23, 59),measurement="test7-meteostat")


