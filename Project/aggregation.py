# Print the statistical features of the sensory data, such
# as the maximum, minimum, average and standard deviation, computed
# every n observations.

from matplotlib.figure import Figure
from io import BytesIO

from utility import proxyData

import pandas as pd
import pybase64

class Aggregation:

	def __init__(self):
		self.df = pd.DataFrame([])
		self.df_total = self.df.copy()
		self.max = None
		self.min = None
		self.mean = None
		self.std = None

	def update_pandas(self):
		self.df = pd.DataFrame(proxyData)
		self.df_total = self.df.copy()
		self.df = self.df.drop(columns=["MAC", "IP", "DeviceId","Time","C_Protocol","GPS","AQI"], axis=1, errors='ignore')
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

	def get_protocol_delay(self, protocol):
		mean = self.df_total[self.df_total["C_Protocol"] == protocol]["Delay"].mean()
		return mean if str(mean) != "nan" else 0

	def get_packet_delivery_ratio(self,protocol):
		try:
			count_value = self.df_total[self.df_total["C_Protocol"] == protocol]["C_Protocol"].count()

			packets = count_value
			total = self.df_total["C_Protocol"].count()

			if total == 0:
				return 0.0
			
			return packets / total

		except:
			return 0.0

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

	def build_graph(self,graph, label, title):
		protocols = ["HTTP","MQTT","COAP"]
		means = []

		if len(list(self.df_total.columns)) == 0:
			means = [0]*3
		else:
			get_graph_data = None

			if graph == "Delay":
				get_graph_data = self.get_protocol_delay
			elif graph == "Ratio":
				get_graph_data = self.get_packet_delivery_ratio
			else:
				get_graph_data = self.get_protocol_delay

			means = [get_graph_data(protocol) for protocol in protocols]

		fig = Figure()
		ax = fig.subplots()
		
		barlist = ax.bar(protocols, means,width = 0.4)
		if graph == "Ratio":
			ax.set_ylim(0.0, 1.0)
		barlist[0].set_color('r')
		barlist[1].set_color('g')
		barlist[2].set_color('b')

		ax.set_ylabel(label)
		ax.set_title(title)

		buf = BytesIO()
		fig.savefig(buf, format="png")
		data = pybase64.b64encode(buf.getbuffer()).decode("ascii")

		buf.seek(0)
		return f"data:image/png;base64,{data}"