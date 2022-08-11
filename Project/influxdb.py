from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

from utility import ArimaCountUpdates, ArimaDFPost, influx_parameters, ArimaCountUpdates, ArimaMaxUpdate, ArimaDFPost
from utility import jsonpost2pandas

import pandas as pd

def influxdb_post(json_data, measurement="",tag_col=[],time_col ="Time"):
    user= influx_parameters["user"]
    token= influx_parameters["token"]
    bucket= influx_parameters["bucket"]
    server= influx_parameters["server"]

    if measurement=="":
        measurement= influx_parameters["measurement"]

    client = InfluxDBClient(url=server, token=token, org=user, timeout=10000)
 
    write_api = client.write_api(write_options=SYNCHRONOUS)

    print("[InfluxDbPost] Data to Post")
    print(json_data)

    json_data.dropna(inplace = True)
    
    if json_data.empty:
        print("[INFLUXDB_POST] EMPTY")
    else:
        # pass
        write_api.write(bucket=bucket, org=user, record=json_data,data_frame_measurement_name=measurement,data_frame_tag_columns=tag_col,data_frame_timestamp_column=time_col)
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
    
    query_real_data = f' from(bucket:"{influx_parameters["bucket"]}")\
    |> range(start: -30d)\
    |> filter(fn:(r) => r["_measurement"] == "{measurement}")\
    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value" )\
    |> keep(columns: ["Device", "GPS", "RSSI" ,"Temperature",  "Humidity", "Gas","AQI","_time"])'


    query_predicted_data = f' from(bucket:"{influx_parameters["bucket"]}")\
    |> range(start: -30d)\
    |> filter(fn:(r) => r["_measurement"] == "{measurement}")\
    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value" )\
    |> keep(columns: ["Device", "GPS","_time","Temperature_predicted","Humidity_predicted","Gas_predicted"])'



    tables_real_data = query_api.query_data_frame(query=query_real_data, org=user)
    tables_predicted_data = query_api.query_data_frame(query=query_predicted_data, org=user)


    # try:
    #     StorageHandler().save_data_csv(tables_real_data, ["Device", "GPS", "RSSI" ,"Temperature",  "Humidity", "Gas","AQI","_time"] ,measurement)
    # except:
    #     pass
    # try:
    #     StorageHandler().save_data_csv(tables_real_data, ["Device", "GPS", "RSSI" ,"Temperature",  "Humidity", "Gas","AQI","_time","Temperature_predicted","Humidity_predicted","Gas_predicted"] ,measurement)
    # except:
    #     pass

    return tables_real_data, tables_predicted_data

def dataframe2series_list(df):
    list_series=[]

    for col in df:
        list_series.append(df[col].squeeze().rename(col))

    return list_series

def get_dataframe_from_influxdb(measurement, drop_columns=["AQI","result","table","RSSI"], masking_device=None):
    def __table_cleaning(table):
        
        if isinstance(table, list):
            table = pd.concat(table)    

        table = table.dropna()
        table = table.drop(columns=drop_columns, axis=1, errors='ignore')
        
        if not table.empty:
            table=table.rename(columns={"_time":"ds"})
            if masking_device!= None:
                mask = table['Device'].str.contains(masking_device)
                table = table[mask]

            table= table.set_index('ds')
        return dataframe2series_list(table)#list_series

    table_real_data, table_predicted_data=influxdb_query(measurement)

    table_real_data = __table_cleaning(table_real_data)
    table_predicted_data = __table_cleaning(table_predicted_data)

    return table_real_data, table_predicted_data

def send_influxdb(json_data, measurement=influx_parameters["measurement"]):
    global ArimaCountUpdates
    global ArimaMaxUpdate
    global ArimaDFPost
    
    json_post = jsonpost2pandas(json_data)
    if ArimaCountUpdates == ArimaMaxUpdate - 1:
        ArimaCountUpdates = 0

        try:
            ArimaDFPost = pd.concat([ArimaDFPost,json_post])
            ArimaDFPost.reset_index(inplace=True, drop=True)
            influxdb_post(ArimaDFPost, measurement=measurement,tag_col=["Device","GPS"]) # IMPORTANTE!!!!
            ArimaDFPost = pd.DataFrame()
        except:
            print("[send_influxdb] exception: post failed")
    else:
        ArimaCountUpdates += 1
        ArimaDFPost = pd.concat([ArimaDFPost,json_post]) # ArimaDFPost.append(json_post)

if __name__=="__main__":
    list_series_real, list_series_predicted=get_dataframe_from_influxdb(measurement=influx_parameters["measurement"])
    
    for serie in list_series_real:
        print()
        print(serie)
        print(serie.shape[0])
        print()
    
    for serie in list_series_predicted:
        print()
        print(serie)
        print(serie.shape[0])
        print()