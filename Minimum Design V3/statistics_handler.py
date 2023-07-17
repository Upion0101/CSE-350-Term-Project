import pandas as pd
import tkinter.messagebox as messagebox


class StatisticsHandler:
    def __init__(self, df):
        self.df = df

    def compute_statistics(self, data_stream):
        if data_stream not in self.df.columns:
            messagebox.showerror("Invalid Data Stream", f"The selected data stream '{data_stream}' does not exist.")
            return

        stream_data = self.df[data_stream]

        statistics = {
            'Min': stream_data.min(),
            'Max': stream_data.max(),
            'Mean': stream_data.mean(),
            'Median': stream_data.median(),
            'Standard Deviation': stream_data.std()
        }

        return pd.Series(statistics)