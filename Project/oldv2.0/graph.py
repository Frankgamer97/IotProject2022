
import mpld3
from mpld3 import plugins
import numpy as np
import matplotlib.pyplot as plt


# creating the dataset
data = {'HTTP':20, 'MQTT':15, 'COAP':30}
protocols = list(data.keys())
values = list(data.values())

fig = plt.figure(figsize = (10, 5))

# creating the bar plot
barlist = plt.bar(protocols, values,
		width = 0.4)
barlist[0].set_color('r')
barlist[1].set_color('g')
barlist[2].set_color('b')

# plt.xlabel("Courses offered")
plt.ylabel("Seconds")
plt.title("Average Delay")
plt.savefig("tmp/delay.jpg")
plt.show()

