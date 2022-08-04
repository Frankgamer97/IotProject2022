from copy import deepcopy
from time import sleep

from threading import Thread
from turtle import left

from statsmodels.tsa.arima_model import ARIMA
from matplotlib.figure import Figure
from io import BytesIO

import pmdarima as pm
import pandas as pd
import numpy as np
import pybase64
#from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.arima.model import ARIMA

from matplotlib import pyplot as plt
from pmdarima.preprocessing import FourierFeaturizer
from sklearn.metrics import mean_squared_error as mse
import pickle
from influxdb import get_dataframe_from_influxdb, influxdb_post
from utility import influxdb_forecast_sample, influx_parameters, influxdb_past_sample

from DataStorage import StorageHandler

import traceback


class Forecast:
        seasonality=365
        #self.dict_model={"temp_arima":None, "hum_arima":None,"gas_arima":None}
        dict_prediction={"temp_arima":None, "hum_arima":None,"gas_arima":None}

        def __init__(self, df,seasonality=True, series_list_predicted = []):
                #self.dict_model={"temp_arima":None, "hum_arima":None,"gas_arima":None}
                self.df =df   #it's a pandaseries
                self.df_original = df
                self.predictions=None #it's a pandaseries
                #self.tuning()
                self.fitted_model=None # it's pdmarima model
                self.mparima_dict={}
                self.seasonality=seasonality
                self.series_list_predicted = series_list_predicted


        def get_seasonality(self):
                self.D=pm.arima.nsdiffs(self.df, max_D=5,m=12)
                return self.D

        def get_stationarity(self):
                self.d=pm.arima.ndiffs(self.df, max_d=5)
                return self.d

        def tuning(self):
                        model=self.df.name
                #for model in Forecast.dict_prediction.keys():
                        StorageHandler.create_tmp_directories()
                        self.mparima_dict[model]=StorageHandler.load_forecast_model(model)
                        if self.mparima_dict[model] is None:
                                print(f"[ARIMA] No {model} found")
                                self.mparima_dict[model]={}
                        else:
                                print(f"[ARIMA] {model} already exists")


                        if self.seasonality==True:
                                four_terms = FourierFeaturizer(Forecast.seasonality, 2)
                                end=len(self.df)
                                start=int(end-Forecast.seasonality)
                                self.df, self.exog = four_terms.fit_transform(self.df[start:end])
                        else:
                                self.exog=None


                        if self.mparima_dict[model]=={}:

                                print(f"[ARIMA] Creating model: {model}")
                                if self.seasonality==True:
                                        arima_model = pm.auto_arima(y=self.df, exogenous=self.exog,start_p=0,d=self.get_stationarity(),start_q=0,
                                                          max_p=2,max_q=2, start_P=0,
                                                          D=self.get_seasonality()+1, start_Q=0, max_P=2,
                                                          max_Q=2, m=12, seasonal=True,
                                                          error_action='warn',trace=True,
                                                          supress_warnings=True,stepwise=True,
                                                          random_state=20,n_fits=50)

                                else:
                                        self.exog=[]
                                        arima_model = pm.auto_arima(y=self.df, start_p=0,d=self.get_stationarity(),start_q=0,
                                                          max_p=2,max_q=2, start_P=0,
                                                          D=1, start_Q=0, max_P=2,
                                                          max_Q=2, m=12, seasonal=True,
                                                          error_action='warn',trace=True,
                                                          supress_warnings=True,stepwise=True,
                                                          random_state=20,n_fits=50)
                                arima_model.summary()

                                #self.mparima_dict[model]={"order":arima_model.order, "seasonal_order":arima_model.seasonal_order,
                                #                        "y_prime":self.y_prime, "exog":self.exog}

                                self.mparima_dict[model]["order"]=arima_model.order
                                self.mparima_dict[model]["seasonal_order"]=arima_model.seasonal_order
                       


                        self.mparima_dict[model]["y_prime"]=self.df
                        self.mparima_dict[model]["exog"]=self.exog
                        
                        StorageHandler.save_forecast_model(self.mparima_dict[model], name=model)


                        #self.mparima_dict[model]=summ
             

        def fit(self, model_name):

                if self.seasonality==True:
                        self.fitted_model=pm.arima.ARIMA(order=self.mparima_dict[model_name]["order"], seasonal_order=self.mparima_dict[model_name]["seasonal_order"], start_params=None,
                         method='lbfgs', maxiter=50, suppress_warnings=True, out_of_sample_size=0, 
                         scoring='mse', scoring_args=None, trend=None, with_intercept=True)
                        self.fitted_model.fit(self.mparima_dict[model_name]["y_prime"], self.mparima_dict[model_name]["exog"])
                else:
                        self.fitted_model=pm.arima.ARIMA(order=self.mparima_dict[model_name]["order"], seasonal_order=self.mparima_dict[model_name]["seasonal_order"], start_params=None,
                         method='lbfgs', maxiter=50, suppress_warnings=True, out_of_sample_size=0, 
                         scoring='mse', scoring_args=None, trend=None, with_intercept=True)
                        self.fitted_model.fit(self.mparima_dict[model_name]["y_prime"])  
                


        def forecast(self,model_name,n_periods,freq="D"):
                if self.seasonality==True:
                        assert n_periods<=Forecast.seasonality
                        exog=self.mparima_dict[model_name]["exog"].dropna()
                        end=len(exog)
                        #print(len(exog))
                        start=int(end-Forecast.seasonality)
                        try:
                                fc = self.fitted_model.predict(n_periods=n_periods,exogenous=exog[start:n_periods])
                        except Exception as e:
                                fc = [np.nan] * n_periods if n_periods > 1 else np.nan
                        last_rev=self.df.index[-1]
                        #date_range= pd.date_range(last_rev+pd.DateOffset(1),last_rev+pd.DateOffset(n_periods), freq=freq)
                        date_range= pd.date_range(last_rev,periods=n_periods+1, freq=freq) [1::]
                        date_forcasted= pd.Series(date_range)
                        #fc_series = pd.Series(fc)
                        self.predictions = pd.Series(list(fc), index=date_forcasted).rename(self.df.name+"_predicted")
                else:
                        '''
                        print()
                        print("[Forecast] start")
                        print(self.df)
                        print(n_periods)
                        print(self.mparima_dict[model_name])
                        print("[Forecast] end")
                        print()
                        '''
                        try:
                                fc = self.fitted_model.predict(n_periods=n_periods)

                        except Exception as e:
                                fc = [np.nan] * n_periods if n_periods > 1 else np.nan
                        '''
                        print("[Forecast]DF=========>")
                        print(self.df)
                        print("[Forecast]DF=========>")
                        
                        print("[Forecast]DFOriginal=========>")
                        print(self.df_original)
                        print("[Forecast]DFOriginal=========>")

                        print("[Forecast]DFindex=========>")
                        print(self.df.index)
                        print("last")
                        print(self.df.index[-1])
                        print("[Forecast]DFindex=========>")

                        print("[Forecast]DFOriginalindex=========>")
                        print(self.df_original.index)
                        print("last")
                        print(self.df_original.index[-1])
                        print("[Forecast]DFOriginalindex=========>")
                        '''

                        last_rev=self.df.index[-1]

                        # print("=============>")
                        # print(last_rev)
                        # print("=============>")

                        date_range= pd.date_range(last_rev,periods=n_periods+1, freq=freq) [1::]

                        # print("[Forecast]Date_range=========>")
                        # print(date_range)
                        # print("[Forecast]Date_range=========>")

                        date_forcasted= pd.Series(date_range)
                        #fc_series = pd.Series(fc)
                        self.predictions = pd.Series(list(fc), index=date_forcasted).rename(self.df.name+"_predicted")

                        
                        # print("[Forecast]Predictions=========>")
                        # print(self.predictions)
                        # print("[Forecast]Predictions=========>")

                return self.predictions
        
        def plot_forecast(self):
                plt.figure(figsize=(12,5), dpi=100)

                plt.plot(self.df_original, label='training',color="darkgreen")
                plt.plot(self.predictions, label='forecast',color='red')


                plt.title(f'Forecast vs Actuals: {self.df.name}')
                plt.legend(loc='upper left', fontsize=8)
                plt.show()
        
        def get_image_result(self):

                local_predictions = deepcopy(self.predictions)
                df = pd.concat(self.series_list_predicted, axis=1)
                df.reset_index(inplace=True)
                df = df.rename(columns = {'ds':'Time'})

                if self.df_original.name+"_predicted" in df.columns:

                        df = df[["Time",self.df_original.name+"_predicted"]]
                        df = df.set_index("Time")

                        df = df.squeeze()
                        
                        local_predictions.name = self.df_original.name+"_predicted"
                        self.concatenated_prediction= pd.concat([df,local_predictions])
                else:
                        self.concatenated_prediction = local_predictions        

                self.concatenated_prediction = self.concatenated_prediction.apply(lambda sorata: round(sorata,1))
                

                fig = Figure(figsize=(12,5), dpi=100)
                
                ax = fig.subplots()


                self.df_original = self.df_original.rename(index="Time")
                self.concatenated_prediction = self.concatenated_prediction.rename(index="Time")

                self.df_original.plot(ax = ax, label='training',color="darkgreen")
                self.concatenated_prediction.plot(ax = ax , label='forecast',color='red')

                ax.set_title(f'Forecast vs Actuals: {self.df_original.name}')
                ax.legend(loc='upper left', fontsize=8)

                buf = BytesIO()
                fig.savefig(buf, format="png")
                data = pybase64.b64encode(buf.getbuffer()).decode("ascii")
                buf.seek(0)
                
                return f"data:image/png;base64,{data}"

class ForecastHandler():

        def __init__(self,measurement=influx_parameters["measurement"],n_periods=influxdb_forecast_sample,maxupdate=influxdb_forecast_sample):
                self.countupdate= 0
                self.maxupdate= maxupdate # quanti ne aspetto prima di postare
                self.prediction_list=[]
                self.df_predicted = None
                self.measurement=measurement
                # self.past_predicted = []
                self.n_predictions=n_periods # quanti ne predico

                self.pred = {}
                self.images = {
                        "Temperature": "",
                        "Gas": "",
                        "Humidity": ""
                }
                self.series_list_predicted = []
                self.image_thread = Thread(target=ForecastHandler.build_image_thread, args=(self,))

        @staticmethod
        def get_data_avg(df,p = influxdb_past_sample):
                
                index_range=df.index.strftime("%Y-%m-%d %H:%M:%S") 
                didx=pd.DatetimeIndex(index_range)
                n_period=p     # didx.shape[0]
                if n_period!=0:
                        diff=0
                        for i in range(n_period):
                                if i<n_period:
                                        diff=diff+(didx[-(i+1)]-didx[-(i+2)]).total_seconds()
                        freq=abs(int(diff/n_period))
                        return str(freq)+"s"

                diff=(didx[-1]-didx[-2]).total_seconds()
                freq=abs(int(diff/(n_period+1)))
                return str(freq)+"s"
                
          
        def get_predictions_list(self):
                # series_list=get_dataframe_from_influxdb(self.measurement)

                for df in self.series_list_real:

                        # print("============")
                        # print(f"DF NAME: {df.name}")
                        # print("============")
                        if "Device" in df.name or "GPS" in df.name:
                                pass # print(f"{df.name} is not to predict")
                        else:
                                
                                # print("=============GET PREDICTION LIST===========>")
                                # print(df)
                                # print("=============GET PREDICTION LIST===========>")

                                # df=df
                                forcast=Forecast(df,seasonality=False, series_list_predicted = self.series_list_predicted)
                                #print("SEASON",forcast.D)
                                #print("STATION",forcast.d)
                                forcast.tuning()
                                forcast.fit(df.name)
                              
                                self.predictions=forcast.forecast(df.name,self.n_predictions,ForecastHandler.get_data_avg(df))
                                # forcast.plot_forecast() ####IMPORTANTE
                                # print("predictions\n")
                                # print(predictions)
                                self.prediction_list.append(self.predictions)
                                self.pred[df.name] = self.predictions

                                

                                # self.images[df.name] = forcast.get_image_result()
                return self.prediction_list


        def get_predicted_df(self):
                self.series_list_real, self.series_list_predicted=get_dataframe_from_influxdb(self.measurement)

                #print("=============ARA ARA===========>")
                #print(series_list)
                #print("=============ARA ARA===========>")
                self.get_predictions_list()
                                
                df_device={}
                for df in self.series_list_real:
                        if "Device" in df.name:
                              df_device=df

                df_gps={}
                for df in self.series_list_real:
                        if "GPS" in df.name:
                              df_gps=df

                df_device_predictions=pd.Series(list(df_device[0:self.n_predictions]), index=self.prediction_list[0].index).rename(df_device.name)
    
                df_gps_predictions=pd.Series(list(df_gps[0:self.n_predictions]), index=self.prediction_list[0].index).rename(df_gps.name)
 

                self.df_predicted=pd.concat([df_device_predictions,df_gps_predictions,self.prediction_list[0],self.prediction_list[1],self.prediction_list[2]],axis=1)
                # print("--------------------------------------------------->")
                self.df_predicted.reset_index(inplace=True)
                self.df_predicted = self.df_predicted.rename(columns = {'index':'Time'})

                '''
                print()
                print("[get-predicted_df] I AM HERE [start]")
                print(self.df_predicted)
                print("[get-predicted_df] I AM HERE [end]")
                print()
                '''
                self.df_predicted["Gas_predicted"] = self.df_predicted["Gas_predicted"].apply(lambda x: int(x) if int(x) >= 0 else 0)
                self.df_predicted["Humidity_predicted"] = self.df_predicted["Humidity_predicted"].apply(lambda x: round(x,1))
                self.df_predicted["Temperature_predicted"] = self.df_predicted["Temperature_predicted"].apply(lambda x: round(x,1)) 
                self.prediction_list = []


               

                df = pd.concat(self.series_list_predicted, axis=1)
                df.reset_index(inplace=True)
                df = df.rename(columns = {'ds':'Time'})

                self.df_original = pd.concat(self.series_list_real, axis=1)
                self.df_original.reset_index(inplace=True)
                self.df_original = self.df_original.rename(columns = {'ds':'Time'})



                # local_predictions = deepcopy(self.predictions)
                self.df_concatenated= None
        
                if "Gas_predicted" in df.columns:

                        # df = df[["Time",self.df_original.name+"_predicted"]]
                        # df = df.set_index("Time")

                        # df = df.squeeze()
                        
                        #local_predictions.name = self.df_original.name+"_predicted"
                        #self.concatenated_prediction= pd.concat([df,local_predictions])
                        self.df_concatenated =pd.concat([df,self.df_predicted])

                else:
                        self.df_concatenated = self.df_predicted        

                # df_concatenated = df_concatenated.apply(lambda x: round(x,1))
                '''
                print("[get_predicted_df][START]ORIGINAL================>")
                print(self.df_original)
                print("[get_predicted_df][END]ORIGINAL==================>")
                

                print("[get_predicted_df][START]PRED================>")
                print(self.df_concatenated)
                print("[get_predicted_df][END]PRED==================>")
                '''

                if self.image_thread.is_alive():
                   self.image_thread.join(0)     

                self.image_thread = Thread(target=ForecastHandler.build_image_thread, args=(self,))
                self.image_thread.start()
                return self.df_predicted


        @staticmethod
        def build_image_thread(forecast_handler):
                image_names = ["Temperature", "Humidity", "Gas"]

                for name in image_names:
                        original_data = forecast_handler.df_original[["Time", name]]
                        predicted_data = forecast_handler.df_concatenated[["Time", name+"_predicted"]]


                        # y_min = min([original_data[name].min(), predicted_data[name+"_predicted"].min()])
                        # y_max = max([original_data[name].max(), predicted_data[name+"_predicted"].max()])

                        # y_min = int(y_min)
                        # y_max = int(round(y_max))
                        fig = Figure(figsize=(12,5), dpi=100)
                        ax = fig.subplots()

                        original_data = original_data.set_index("Time").squeeze()
                        predicted_data = predicted_data.set_index("Time").squeeze()


                        out_mse=mse(original_data[-forecast_handler.n_predictions::].tolist(),predicted_data[-forecast_handler.n_predictions::].tolist())
                        out_mse= round(out_mse,4)
                        print(f"---mse:{name}---") 
                        print(out_mse)
                        print(f"---mse:{name}---") 
                        print()
                        original_data.plot(ax = ax, label='training',color="darkgreen")
                        predicted_data.plot(ax = ax , label='forecast',color='red')

                        ax.set_title(f'Forecast vs Actuals: {name}')
                        ax.text( 0.85, 1, "MSE: "+str(out_mse), horizontalalignment="left", verticalalignment="bottom",size=15, color='black', transform=ax.transAxes)
                        ax.legend(loc='upper left', fontsize=8)
                        # ax.set_ylim(y_min, y_max)
                        # y_range = np.arange(y_min, y_max+1)
                        # y_range = list(y_range)
                        # ax.set_yticks(y_range)

                        buf = BytesIO()
                        fig.savefig(buf, format="png")
                        data = pybase64.b64encode(buf.getbuffer()).decode("ascii")
                        buf.seek(0)
                        forecast_handler.images[name] = f"data:image/png;base64,{data}"

        
        def set_past_prediction(self):
                # print("[PREDICTED]================>")

                df = pd.concat(self.series_list_predicted, axis=1)
                df.reset_index(inplace=True)
                df = df.rename(columns = {'ds':'Time'})

                # print(df)
                # print("[PREDICTED-END]============>")
                # print(self.df_predicted)
                # print("===========================>")
                self.concatenated_prediction= pd.concat([df,self.df_predicted])#, ignore_index=True, sort=False)  
                # print("SONO qUII") 
                # print(self.concatenated_prediction)
                # print("SONO qUII")
                
        
        def post_predictions(self):
                # sleep(influxdb_forecast_sample * 1.5)
                influxdb_post(self.df_predicted, measurement=self.measurement,tag_col=["Device","GPS"])





        def send_updates(self):
                self.get_predicted_df()
                self.set_past_prediction()
                self.post_predictions()

        def arima_updates(self):
                if self.countupdate == self.maxupdate -1:
                        self.countupdate = 0
                        try:
                                self.send_updates()
                        except Exception as e:
                                print("Too few observations to estimate starting parameters")
                                print(str(e))

                                print()
                                print()
                                traceback.print_exc()
                                print()
                                print()
                else:
                        self.countupdate += 1



if __name__=="__main__":
        # measurement="test-july27-26"
        handler=ForecastHandler(influx_parameters["measurement"])
        handler.send_updates()