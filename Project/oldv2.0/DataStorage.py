import os
import csv
import pickle
class StorageHandler():



    FORECAST_MODEL_FILE_NAME = "forecast_model.pkl"


    @staticmethod
    def __load_pickle(file_name: str, folder: str):
        file = os.path.join(folder, file_name)
        if not os.path.exists(file):
            return None
        with open(file, "rb") as f:
            return pickle.load(f)


    @staticmethod
    def __save_pickle(obj, file_name: str, folder: str):
        file = os.path.join(folder, file_name)

        with open(file, "wb") as f:
            pickle.dump(obj, f)

    @staticmethod
    def __save_csv(obj, columns,file_name: str, folder: str):
        file = os.path.join(folder, file_name)
        obj.to_csv(file+".csv", columns=columns )
    



    @staticmethod
    def __cd_parent(file):
        return os.path.dirname(file)

    @staticmethod
    def __get_project_directory():
        return StorageHandler.__cd_parent(os.path.realpath(__file__))



    @staticmethod
    def __get_tmp_dir():
        return os.path.join(StorageHandler.__get_project_directory(), "tmp")

    @staticmethod
    def __get_forecast_model_dir():
        return os.path.join(StorageHandler.__get_project_directory(), "data", "forecast_model")

    @staticmethod
    def __get_data_raw_dir():
        return os.path.join(StorageHandler.__get_project_directory(), "data", "raw")


    @staticmethod
    def create_tmp_directories():
        if not os.path.exists(StorageHandler.__get_tmp_dir()):
            os.mkdir(StorageHandler.__get_tmp_dir())

        if not os.path.exists(StorageHandler.__get_forecast_model_dir()):
            os.makedirs(StorageHandler.__get_forecast_model_dir())

        if not os.path.exists(StorageHandler.__get_data_raw_dir()):
            os.makedirs(StorageHandler.__get_data_raw_dir())


    @staticmethod
    def save_forecast_model(forecast_model, name="forecast_model"):
        StorageHandler.__save_pickle(forecast_model, name, StorageHandler.__get_forecast_model_dir())
    
    @staticmethod
    def load_forecast_model(name="forecast_model"):
        return StorageHandler.__load_pickle(name, StorageHandler.__get_forecast_model_dir())



    @staticmethod
    def save_data_csv(csv_table, col=None,name="csv_name"):
        StorageHandler.__save_csv(csv_table, col,name, StorageHandler.__get_data_raw_dir())