from argparse import ArgumentParser

protocols=["any","http","mqtt","coap"]
topics=["any","temperature","humidity","gas","RSSI"]
commands=["visualize", "aggregate","save","translate"]

parser=ArgumentParser()

parser.add_argument("-protocol",dest="srcprotocol", type=str, default="any")
parser.add_argument("-host",dest="host", type=str, default="broker.emqx.io")
parser.add_argument("-topic",dest="topic", type=str, default="any")
parser.add_argument("-command",dest="command", type=str, default="visualize")
parser.add_argument("-n",dest="window", type=int, default=5)
parser.add_argument("-influxconf",dest="influxconf", type=str, default=None)
parser.add_argument("-dstprotocol",dest="dstprotocol", type=str, default=None)
parser.add_argument("-config",dest="config", type=str, default=None)

args = parser.parse_args()

print()
print(args.srcprotocol)
print(args.host)
print(args.topic)
print(args.command)
print(args.window)
print(args.influxconf)
print(args.topic)
print(args.dstprotocol)
print(args.config)
print()

assert args.srcprotocol in protocols
assert args.topic in topics
assert args.command in commands

assert args.command != "save" or args.influxconf is not None
assert args.command != "translate" or args.dstprotocol is not None
