from utility import influx_parameters 
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


def get_point(json_data,type_data,measurement="mamma"):

    print(json_data)

    point = None


    if type_data == "meteostat":
        GPS= json_data["GPS"]
        Temperature = json_data["Temperature"]
        Time = json_data["Time"]

        point = Point(measurement) \
            .tag("GPS", GPS) \
            .field("Temperature", Temperature) \
            .time(Time, WritePrecision.NS)

    elif type_data == "forecasted_data":
        pass

    else:
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



def influxdb_post(json_data, type_data="my_data", measurement=""):
    

    user= influx_parameters["user"]
    token= influx_parameters["token"]
    bucket= influx_parameters["bucket"]
    server= influx_parameters["server"]
    if measurement=="":
        print("sono qui")
        measurement= influx_parameters["measurement"]



    client = InfluxDBClient(url=server, token=token, org=user)

    write_api = client.write_api(write_options=SYNCHRONOUS)

    
    point = get_point(json_data,type_data,measurement)


    #point = Point("my_measurement").tag("location", "Prague").field("temperature", 25.3)
    write_api.write(bucket, user, point)
 
    return "ok"

