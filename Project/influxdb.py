from utility import influx_parameters 
#from influxdb import DataFrameClient
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from DataStorage import StorageHandler
import pandas as pd



def influxdb_post(json_data, measurement="",tag_col=[],time_col ="Time"):
    

    user= influx_parameters["user"]
    token= influx_parameters["token"]
    bucket= influx_parameters["bucket"]
    server= influx_parameters["server"]
    if measurement=="":
        measurement= influx_parameters["measurement"]


    client = InfluxDBClient(url=server, token=token, org=user)
 
    write_api = client.write_api(write_options=SYNCHRONOUS)

    print(json_data)
    print(measurement)

    # write_api.write(bucket=bucket, org=user, record=json_data,data_frame_measurement_name=measurement,data_frame_tag_columns=tag_col,data_frame_timestamp_column=time_col)
    ###### IMPORTANTE
    print("mhhhhinizio")
    return "ok"

def influxdb_query(measurement=""):
    user= influx_parameters["user"]
    token= influx_parameters["token"]
    bucket= influx_parameters["bucket"]
    server= influx_parameters["server"]
    if measurement=="":
        measurement= influx_parameters["measurement"]


    client = InfluxDBClient(url=server, token=token, org=user)
    query_api = client.query_api()

    query = """from(bucket: "esp32")
      |> range(start: -30d)
      |> filter(fn: (r) => r["_measurement"] == "Weather")
      |> filter(fn: (r) => r["GPS"] == "44.49-11.313")
      |> filter(fn: (r) => r["ID"] == "1")
      |> filter(fn: (r) => r["_field"] == "AQI" or r["_field"] == "gas" or r["_field"] == "humidity" or r["_field"] == "temperature" or r["_field"] == "wifi")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value" )
      |> keep(columns: ["Device", "GPS", "RSSI" ,"Temperature",  "Humidity", "Gas","AQI","_time"])
      """

  #  query_api = client.query_api()

    query = f' from(bucket:"{influx_parameters["bucket"]}")\
    |> range(start: -30d)\
    |> filter(fn:(r) => r["_measurement"] == "{measurement}")\
    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value" )\
    |> keep(columns: ["Device", "GPS", "RSSI" ,"Temperature",  "Humidity", "Gas","AQI","_time"])'

    #print(query)


    tables = query_api.query_data_frame(query=query, org=user)
    #print(type(tables))



    try:
        StorageHandler().save_data_csv(tables, ["Device", "GPS", "RSSI" ,"Temperature",  "Humidity", "Gas","AQI","_time"] ,measurement)
    except:
        pass
    return tables


def dataframe2series_list(df,name):

    list_series=[]
    for col in df:
        list_series.append(df[col].squeeze().rename(col))

    return list_series




def get_dataframe_from_influxdb(measurement, drop_columns=["AQI","result","table","RSSI"],masking_device=None,name="my_data_"):
    table=influxdb_query(measurement)
    table = table.dropna()
    
    print("=============>")
    print(table)
    print("=============>")
    

    table = table.drop(columns=drop_columns, axis=1, errors='ignore')
    table=table.rename(columns={"_time":"ds"})
    table_notime=table.drop(columns=["_time"], axis=1, errors='ignore')
    #print(table)
    #print(table_notime)
    if masking_device!= None:
        mask = table['Device'].str.contains(masking_device)
        table = table[mask]
        #table_NonAccl = table[~mask]

    df= table.set_index('ds')#.drop(columns=["Device"], axis=1, errors='ignore')
    # df=df.dropna()
    #print(df)


    return dataframe2series_list(df,name)#list_series


if __name__=="__main__":

    list_series=get_dataframe_from_influxdb(measurement="test-july27-3")
    for serie in list_series:
        print()
        print(serie)
        print(serie.shape[0])
        print()