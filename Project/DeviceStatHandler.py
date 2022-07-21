from threading import Thread
from time import sleep
import pandas as pd
from datetime import datetime
from utility import stat_data_timeout, stat_data_intervall

class DeviceStatHandler:
    __columns = ["Mac","Protocol","Frequency","Delay","Ratio"]
    table = pd.DataFrame(columns=__columns).set_index("Mac")
    chrono_updates = {
        "http": {},
        "coap": {},
        "mqtt": {}
    }
    # updates = stat_data_frequency
    start_time = None

    def __init__(self):
        pass

    @staticmethod 
    def __build_row(json_data, packet_delay, protocol):
        data ={
            "Mac": [json_data["MAC"]],
            "Protocol": [protocol],
            "Frequency": [json_data["Frequency"]],
            "Delay": [packet_delay],
            "Ratio": [1]
        }

        return pd.DataFrame(data)

    @staticmethod
    def update(json_data, packet_delay, protocol):

        # DeviceStatHandler.updates -= 1
        data = DeviceStatHandler.__build_row(json_data, packet_delay, protocol)
        chrono = DeviceStatHandler.chrono_updates 
        
        mac = data["Mac"].to_list()[0]
        protocol = data["Protocol"].to_list()[0] 
        data_delay = data["Delay"].to_list()[0]
        data_ratio = data["Ratio"].to_list()[0]

        df = DeviceStatHandler.table

        # print("CURRENT MAC: ",mac)
        # print("LIST: ",list(df.index))
        
        if mac not in list(df.index):
            print("UNA VVOLTA")
            chrono[protocol][mac] = [datetime.now(), datetime.now()]    
            df = pd.concat([df, pd.DataFrame(data)], ignore_index=True, axis=0).set_index("Mac")
        else:
            chrono[protocol][mac].insert(1,datetime.now())
            df.loc[mac]["Delay"] = data_delay

            if (chrono[protocol][mac][1] - chrono[protocol][mac][0]).seconds < stat_data_intervall:
                df.loc[mac]["Ratio"] += data_ratio
            else:
                chrono[protocol][mac][0] = chrono[protocol][mac][1]
                df.loc[mac]["Ratio"] = data_ratio

        DeviceStatHandler.table = df

        print()
        print(DeviceStatHandler.table)
        print()

    
    @staticmethod
    def get_average_delay(protocol):
        df = DeviceStatHandler.table
        return df[df["Protocol"] == protocol]["Delay"].mean()
    
    @staticmethod
    def get_average_ratio(protocol, frequency):
        df = DeviceStatHandler.table
        df_app = df[df["Protocol"] == protocol]

        return df_app[df_app["Frequency"] == frequency]["Ratio"].mean()

    @staticmethod
    def control_updates():
        # DeviceStatHandler.start = datetime.now()
        def __deamon():
            while True:
                sleep(stat_data_intervall)
                #if True:# if DeviceStatHandler.updates <= 0:
                # DeviceStatHandler.updates = stat_data_frequency
                current = datetime.now()
                
                device_to_delete = []
                
                for protocol, data in DeviceStatHandler.chrono_updates.items():
                    for device, updates in data.items():
                        if (current - updates[1]).seconds > stat_data_timeout:
                            device_to_delete.append((protocol, device))

                for protocol, device in device_to_delete:
                    # print("TO DELETE: ")
                    # print(type(protocol))
                    # print(protocol)
                    # print()
                    # print(type(device))
                    # print(device)
                    del DeviceStatHandler.chrono_updates[protocol][device]
                    print("HERE")
                    DeviceStatHandler.table = DeviceStatHandler.table.drop([device])
                    # print(list(DeviceStatHandler.table.index))
                    print("CURRENT SITUATION")
                    print(DeviceStatHandler.table)

                            
        deamon = Thread(target=__deamon)
        deamon.daemon=True
        deamon.start()
        return deamon