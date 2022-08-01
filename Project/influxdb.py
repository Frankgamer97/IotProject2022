from utility import influx_parameters 
#from influxdb import DataFrameClient
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from DataStorage import StorageHandler
import pandas as pd



def get_point(json_data,type_data,measurement="test-data1"):
    print()#"----------------------INFLUX POST START----------------------")
    print(json_data)
    print()#"----------------------INFLUX POST END----------------------")

    point = None


    if type_data == "meteostat":
        GPS= json_data["GPS"]
        Temperature = json_data["Temperature"]
        Time = json_data["Time"]

        point = Point(measurement) \
            .tag("Device", "meteostat") \
            .tag("GPS", GPS) \
            .field("Temperature", Temperature) \
            .time(Time, WritePrecision.NS)


    elif type_data == "forecasted_meteostat":

        device = json_data["meteostat_Device_predictions"]
        GPS= json_data["meteostat_GPS_predictions"]
        Temperature = json_data["meteostat_Temperature_predictions"]
        Time = json_data["Time"]


        
        point = Point(measurement) \
            .tag("Device", device) \
            .tag("GPS", GPS) \
            .field("Temperature_predicted", Temperature) \
            .time(Time, WritePrecision.NS)


    elif type_data == "forecasted_data":
        mac = json_data["my_data_Device_predictions"]
        GPS= json_data["my_data_GPS_predictions"]
        Temperature = json_data["my_data_Temperature_predictions"]
        Humidity = json_data["my_data_Humidity_predictions"]
        Gas = json_data["my_data_Gas_predictions"]
        Time = json_data["Time"]


        
        point = Point(measurement) \
            .tag("Device", mac) \
            .tag("GPS", GPS) \
            .field("Temperature_predicted", Temperature) \
            .field("Humidity_predicted", Humidity) \
            .field("Gas_predicted", Gas) \
            .time(Time, WritePrecision.NS)

    elif type_data == "my_data":
        mac = json_data["MAC"]
        GPS= json_data["GPS"]
        rssi = json_data["RSSI"]
        Temperature = json_data["Temperature"]
        Humidity = json_data["Humidity"]
        Gas = json_data["Gas"]
        AQI = json_data["AQI"]
        Time = json_data["Time"]


        
        point = Point(measurement) \
            .tag("Device", mac) \
            .tag("GPS", GPS) \
            .field("RSSI", rssi) \
            .field("Temperature", Temperature) \
            .field("Humidity", Humidity) \
            .field("Gas", Gas) \
            .field("AQI", AQI) \
            .time(Time, WritePrecision.NS)

    return point

def influxdb_post_copy(json_data, type_data="my_data", measurement="",single_point=True,tag_columns=[],field_columns =[]):
    

    user= influx_parameters["user"]
    token= influx_parameters["token"]
    bucket= influx_parameters["bucket"]
    server= influx_parameters["server"]
    if measurement=="":
        measurement= influx_parameters["measurement"]

    if single_point:   

        client = InfluxDBClient(url=server, token=token, org=user)
     
        write_api = client.write_api(write_options=SYNCHRONOUS)

        point = get_point(json_data,type_data,measurement)

        #point = Point("my_measurement").tag("location", "Prague").field("temperature", 25.3)
        write_api.write(bucket, user, point)
    else:


        client = InfluxDBClient(url=server, token=token, org=user)
     
        write_api = client.write_api(write_options=SYNCHRONOUS)

        #point = get_point(json_data,type_data,measurement)

        #point = Point("my_measurement").tag("location", "Prague").field("temperature", 25.3)
        #print(json_data)

        



        #write_api.write(bucket=bucket, org=user, record=json_data,data_frame_measurement_name=measurement,data_frame_tag_columns=tag_columns,data_frame_timestamp_column=["Time"])


    #    client = DataFrameClient(url=server, token=token, org=user)
    #    protocol = 'json'
    #    client.write_points(json_data, measurement, protocol=protocol,tag_columns=tag_columns,field_columns =field_columns)
 
    return "ok"

def influxdb_post_1(json_data, type_data="my_data", measurement="",single_point=True,tag_columns=[],field_columns =[]):
    

    user= influx_parameters["user"]
    token= influx_parameters["token"]
    bucket= influx_parameters["bucket"]
    server= influx_parameters["server"]
    if measurement=="":
        measurement= influx_parameters["measurement"]


    if single_point:   
        print("NOOOOOOOOOOO")

        client = InfluxDBClient(url=server, token=token, org=user)
     
        write_api = client.write_api(write_options=SYNCHRONOUS)

        point = get_point(json_data,type_data,measurement)

        #point = Point("my_measurement").tag("location", "Prague").field("temperature", 25.3)
        write_api.write(bucket, user, point)
    else:
        print("SIIIIIIIIIII")

        client = InfluxDBClient(url=server, token=token, org=user)
     
        write_api = client.write_api(write_options=SYNCHRONOUS)

        #point = get_point(json_data,type_data,measurement)

        #point = Point("my_measurement").tag("location", "Prague").field("temperature", 25.3)
        #for el in json_data:
        #    print(el)

        print(json_data)
        table=pd.DataFrame(json_data)
        print(table)
        '''
        dt2=pd.to_datetime(table["Time"],format="%d/%m/%Y",unit='ns')
        dta=pd.date_range("2020-12-1","2022-07-1",freq="D")
        print("TYEP")
        print(type(dt2))
        print(type(dta))
        print(dt2)
        table["Time"]=dt2
      

        #table.set_index('Time', inplace=True)# Transform index to PeriodIndex
        #table.index = pd.to_datetime(table.index, unit='s')
        #table.index.name="Time"

        #ts = pd.to_datetime(str(dt2)) 
        d = dta.strftime('%d-%m-%Y')
        print("----------------------------------------------------------------------------------------------------------")
        print((d))
        table["Time"]=dta
        #table["Time"]=d
        print(table)
        print(measurement)
'''


        write_api.write(bucket=bucket, org=user, record=table,data_frame_measurement_name=measurement,data_frame_tag_columns=tag_columns,data_frame_timestamp_column="Time")


    #    client = DataFrameClient(url=server, token=token, org=user)
    #    protocol = 'json'
    #    client.write_points(json_data, measurement, protocol=protocol,tag_columns=tag_columns,field_columns =field_columns)
 
    return "ok"






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

'''

def influxdb_get(measurement="",drop_columns=[],masking_device=None):

    table=influxdb_query(measurement).drop(columns=drop_columns, axis=1, errors='ignore')
    table=table.rename(columns={"_time":"ds"})
    table_notime=table.drop(columns=["_time"], axis=1, errors='ignore')


    if masking_device!= None:
        mask = table['Device'].str.contains(masking_device)
        table = table[mask]
        table_NonAccl = table[~mask]
    table= table.set_index('ds')#.drop(columns=["Device"], axis=1, errors='ignore')
    return table

'''

def dataframe2series_list(df,name):

    list_series=[]
    for col in df:
        list_series.append(df[col].squeeze().rename(col))

    return list_series




def get_dataframe_from_influxdb(measurement, drop_columns=["AQI","result","table","RSSI"],masking_device=None,name="my_data_"):
    table=influxdb_query(measurement).drop(columns=drop_columns, axis=1, errors='ignore')
    table=table.rename(columns={"_time":"ds"})
    table_notime=table.drop(columns=["_time"], axis=1, errors='ignore')
    #print(table)
    #print(table_notime)
    if masking_device!= None:
        mask = table['Device'].str.contains(masking_device)
        table = table[mask]
        #table_NonAccl = table[~mask]

    df= table.set_index('ds')#.drop(columns=["Device"], axis=1, errors='ignore')
    df=df.dropna()
    #print(df)


    return dataframe2series_list(df,name)#list_series


if __name__=="__main__":

    list_series=get_dataframe_from_influxdb(measurement="test-july27-3")
    for serie in list_series:
        print()
        print(serie)
        print(serie.shape[0])
        print()