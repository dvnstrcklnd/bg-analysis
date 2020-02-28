import os
import pandas as pd
import numpy as np
import json

from copy import deepcopy

import plotly.express as px
import plotly.graph_objects as go
from IPython.core.display import display, HTML

class TidepoolExplorer():
    
    def __init__(self, folder='.'):
        self.folder = folder
        self.data = self.read_tp_json()
        
    def read_tp_json(self, filename='blip-input.json'):
        path = os.path.join(self.folder, filename)
        with open(path) as f:
            data = json.load(f)
            
        return data
    
    def cbg_data(self):
        return [d for d in self.data if d['type'] == 'cbg']

class DexcomExplorer():
    
    def __init__(self, folder='.'):
        self.folder = folder
        data = self.read_csv()
        self.event_data = self.clean_dataframe(data)
        self.bg_data = self.get_bg_data()
    
    def get_bg_data(self):
        bg_mask = (self.event_data['Event Type'] == 'EGV')
        bg_data = self.event_data.loc[bg_mask]
        diffs = bg_data[['Timestamp', "Glucose Value (mg/dL)"]].diff()
        diffs['minutes'] = diffs['Timestamp'].dt.total_seconds() / 60
        bg_data['derivative'] = diffs.apply(lambda row: self.rate_of_change(row), axis=1)
        return bg_data
        
    def read_csv(self):
        filenames = os.listdir(self.folder)
        csv_filenames = [f for f in filenames if f.endswith('.csv')]

        frames = []
        for fn in csv_filenames:
            with open(fn) as f:
                print("reading {}".format(fn))
                frame = pd.read_csv(f).rename(columns={"Timestamp (YYYY-MM-DDThh:mm:ss)": "Timestamp"})
                frame["Timestamp"] = pd.to_datetime(frame["Timestamp"])
                frames.append(frame.drop(['Index'], axis=1))
                
        return pd.concat(frames, ignore_index=True)
    
    @staticmethod
    def clean_dataframe(dataframe):
        dataframe = dataframe.drop_duplicates(['Transmitter Time (Long Integer)','Transmitter ID'])

        dataframe["Glucose Value (mg/dL)"] = dataframe["Glucose Value (mg/dL)"].astype('str')
        numeric_mask = (dataframe["Glucose Value (mg/dL)"].str.match(r"[\d\.]+"))
        dataframe = dataframe.loc[numeric_mask]
        dataframe["Glucose Value (mg/dL)"] = dataframe["Glucose Value (mg/dL)"].astype('float32')
        return dataframe.sort_values(by=['Timestamp'])
                
    @staticmethod
    def rate_of_change(row):
        return row["Glucose Value (mg/dL)"] / row['minutes'] if row['minutes'] > 4 else np.nan
    
    def plot_summary(self, plot_window_data, all_stats):
        fig = go.Figure()
        fig.add_trace(go.Scatter(
                        x=plot_window_data['Timestamp'],
                        y=plot_window_data["Glucose Value (mg/dL)"],
                        name='points',
                        line_color='lightgray',
                        opacity=0.5))

        # fig.add_trace(go.Scatter(
        #                 x=all_stats.date,
        #                 y=all_stats['max'],
        #                 name='max',
        #                 line_color='lightgray',
        #                 opacity=0.4))

        fig.add_trace(go.Scatter(
                        x=all_stats.date,
                        y=all_stats['90%'],
                        name='90%',
                        line_color='orange',
                        opacity=0.5))

        # fig.add_trace(go.Scatter(
        #                 x=all_stats.date,
        #                 y=all_stats['mean'],
        #                 name='mean',
        #                 line_color='darkgray',
        #                 opacity=1))

        fig.add_trace(go.Scatter(
                        x=all_stats.date,
                        y=all_stats['50%'],
                        name='50%',
                        line_color='darkgray',
                        opacity=1))

        fig.add_trace(go.Scatter(
                        x=all_stats.date,
                        y=all_stats['10%'],
                        name='10%',
                        line_color='red',
                        opacity=0.5))

        # fig.add_trace(go.Scatter(
        #                 x=all_stats.date,
        #                 y=all_stats['min'],
        #                 name='min',
        #                 line_color='lightgray',
        #                 opacity=0.4))

        fig.update_layout(title_text="Blood Glucose Summary",
                          xaxis_rangeslider_visible=True,
                          template="plotly_white",
                          yaxis_range=[0,400],
                          yaxis_dtick=50,
                          xaxis_title="Date",
                          yaxis_title="BG (mg/dL)"
                         )
        fig.show()