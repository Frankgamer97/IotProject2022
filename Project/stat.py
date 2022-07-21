import pandas as pd

df = pd.DataFrame(columns=["Mac","Protocol","Frequency","Delay","Ratio"])
df.set_index("Mac")

df["Mac"].astype(str)
df["Protocol"].astype(str)
df["Frequency"].astype(int)
df["Delay"].astype(int)
df["Ratio"].astype(int)

data = {
    "Mac": ["mac1"],
    "Protocol": ["http"],
    "Frequency": [3000],
    "Delay": [12],
    "Ratio": [5]
}

data2 = {
    "Mac": ["mac2"],
    "Protocol": ["mqtt"],
    "Frequency": [3000],
    "Delay": [12],
    "Ratio": [3]
}

data3 = {
    "Mac": ["mac3"],
    "Protocol": ["coap"],
    "Frequency": [3000],
    "Delay": [12],
    "Ratio": [4]
}
data4 = {
    "Mac": ["mac4"],
    "Protocol": ["coap"],
    "Frequency": [5000],
    "Delay": [36],
    "Ratio": [7]
}



df = pd.concat([df,pd.DataFrame(data)], ignore_index=True, axis=0)
df = pd.concat([df,pd.DataFrame(data2)], ignore_index=True, axis=0)
df = pd.concat([df,pd.DataFrame(data3)], ignore_index=True, axis=0)
df = pd.concat([df,pd.DataFrame(data4)], ignore_index=True, axis=0)
df = df.set_index("Mac")
print(df)
print()
print(type(df.loc["mac4"]))
print(df.loc["mac4"])
print()
print(type(df.loc["mac4"].tolist()))
print(df.loc["mac4"].tolist())
print()
print(type(df.index))
print(list(df.index))
print()
df.loc["mac4"]["Ratio"]=99
#print(df)
# df_app = df[df["Protocol"] == "coap"]
# print(df_app[df_app["Frequency"] == 3000])

df = df.drop(["mac4"])
print(df)