from utility import influx_parameters 


def influxdb_post(json_data):
    

    user= influx_parameters["user"]
    token= influx_parameters["token"]
    bucket= influx_parameters["bucket"]
    server= influx_parameters["server"]
    measurement= influx_parameters["measurement"]



    client = InfluxDBClient(url=server, token=token, org=user)

    write_api = client.write_api(write_options=SYNCHRONOUS)


    mac = json_data["MAC"]
    GPS= json_data["GPS"]
    rssi = json_data["RSSI"]
    Temperature = json_data["Temperature"]
    Humidity = json_data["Humidity"]
    Gas = json_data["Gas"]
    AQI = json_data["AQI"]
    Time = json_data["Time"]
    

    print(json_data)
    
    point = Point(measurement) \
        .tag("Device", mac) \
        .tag("GPS", GPS) \
        .field("RSSI", rssi) \
        .field("Temperature", Temperature) \
        .field("Humidity", Humidity) \
        .field("Gas", Gas) \
        .field("AQI", AQI) \
        .time(Time, WritePrecision.NS)


    #point = Point("my_measurement").tag("location", "Prague").field("temperature", 25.3)
    write_api.write(bucket, user, point)
 
    return "ok"

