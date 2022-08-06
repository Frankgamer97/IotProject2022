from utility import influx_parameters, influxdb_countupdates, influxdb_maxupdate, influxdb_df_post
from utility import jsonpost2pandas
#from influxdb import DataFrameClient
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.util import date_utils
from influxdb_client.client.util.date_utils import DateHelper

from DataStorage import StorageHandler
from dateutil.tz import tzlocal
import pandas as pd



def influxdb_post(json_data, measurement="",tag_col=[],time_col ="Time"):
    

    user= influx_parameters["user"]
    token= influx_parameters["token"]
    bucket= influx_parameters["bucket"]
    server= influx_parameters["server"]
    if measurement=="":
        measurement= influx_parameters["measurement"]

    # date_utils.date_helper = DateHelper(timezone=tzlocal())
    client = InfluxDBClient(url=server, token=token, org=user, timeout=10000)
 
    write_api = client.write_api(write_options=SYNCHRONOUS)

    print(json_data)

    json_data.dropna(inplace = True)
    
    if json_data.empty:
        print("[INFLUXDB_POST] EMPTY")
    else:
        # pass
        write_api.write(bucket=bucket, org=user, record=json_data,data_frame_measurement_name=measurement,data_frame_tag_columns=tag_col,data_frame_timestamp_column=time_col)
    
    ###### IMPORTANTE
    return "ok"

def influxdb_query(measurement=""):
    user= influx_parameters["user"]
    token= influx_parameters["token"]
    bucket= influx_parameters["bucket"]
    server= influx_parameters["server"]
    if measurement=="":
        measurement= influx_parameters["measurement"]

    # date_utils.date_helper = DateHelper(timezone=tzlocal())
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

    #print(query)


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
    # table=influxdb_query(measurement)
    def __table_cleaning(table):
        
        '''
        print("=============>")
        print(type(table))
        print(table)
        print("=============>")
        '''
        if isinstance(table, list):
            table = pd.concat(table)    

        table = table.dropna()
        # print(measurement)
        # print("=============>")
        
        

        table = table.drop(columns=drop_columns, axis=1, errors='ignore')
        if not table.empty:
            table=table.rename(columns={"_time":"ds"})
            # table_notime=table.drop(columns=["_time"], axis=1, errors='ignore')
            #print(table)
            #print(table_notime)
            if masking_device!= None:
                mask = table['Device'].str.contains(masking_device)
                table = table[mask]
                #table_NonAccl = table[~mask]

            table= table.set_index('ds')#.drop(columns=["Device"], axis=1, errors='ignore')
            # df=df.dropna()
            #print(df)


        return dataframe2series_list(table)#list_series

    table_real_data, table_predicted_data=influxdb_query(measurement)

    table_real_data = __table_cleaning(table_real_data)
    table_predicted_data = __table_cleaning(table_predicted_data)

    return table_real_data, table_predicted_data

def send_influxdb(json_data, measurement=influx_parameters["measurement"]):

    global influxdb_countupdates
    global influxdb_maxupdate
    global influxdb_df_post
    
    json_post = jsonpost2pandas(json_data)
    if influxdb_countupdates == influxdb_maxupdate - 1:
        influxdb_countupdates = 0

        try:
            influxdb_df_post = influxdb_df_post.append(json_post)
            influxdb_df_post.reset_index(inplace=True, drop=True)
            influxdb_post(influxdb_df_post, measurement=measurement,tag_col=["Device","GPS"]) # IMPORTANTE!!!!
            influxdb_df_post = pd.DataFrame()
        except:
            print("[send_influxdb] exception: post failed")
            pass
    else:
        influxdb_countupdates += 1
        influxdb_df_post = influxdb_df_post.append(json_post)

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
