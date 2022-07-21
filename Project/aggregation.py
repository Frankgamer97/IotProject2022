# Print the statistical features of the sensory data, such
# as the maximum, minimum, average and standard deviation, computed
# every n observations, where n is a tunable parameters.

from utility import listvalues
from utility import set_tunable_window

import pandas as pd
import numpy as np




class Aggregation:

	def __init__(self):
		self.df = pd.DataFrame([])
		self.max = None
		self.min = None
		self.mean = None
		self.std = None




	def update_pandas(self):
		self.df = pd.DataFrame(listvalues)
		self.df_total = self.df.copy()
		self.df = self.df.drop(columns=["MAC","Time","C_Protocol","GPS","AQI"], axis=1, errors='ignore')
		self.df = self.df.apply(pd.to_numeric, errors='coerce')


	def get_pandas(self):
		return self.pandas

	def get_max(self):
		self.max = self.df.max()
		return self.max.to_dict()


	def get_min(self):
		self.min = self.df.min()
		return self.min.to_dict()


	def get_mean(self):
		self.mean = self.df.mean()
		return self.mean.to_dict()

	def get_std(self):
		self.std = self.df.std()
		return self.std.to_dict()

	def get_var(self):
		self.var = self.df.var()
		return self.var.to_dict()

	def get_cov(self):
		self.cov = self.df.cov()
		return self.cov.to_dict()

	def get_packet_delivery_ratio(self,protocol):
		try:
			packets = 1 + self.df_total[self.df_total["C_Protocol"] == protocol]["C_Protocol"].count()
			total = 1 + self.df_total["C_Protocol"].count()

			return packets / total

		except:
			return 1.0

	def build_aggregate(self):
		self.update_pandas()
		max = self.get_max()
		min = self.get_min()
		mean = self.get_mean()
		std = self.get_std()

		if not self.df.empty:
			return {"max":max, "min":min, "mean":mean, "std":std}
		else:
			return {} 