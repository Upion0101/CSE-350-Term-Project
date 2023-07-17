import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import style
import pandas as pd
import os
import pytz
from datetime import datetime, timedelta
from tzlocal import get_localzone


# Apply custom style
style.use('ggplot')

class DataVisualizer:

    def __init__(self, window):
        self.window = window
        self.window.title("RogerWare Prototype")

        self.fig = Figure(figsize=(5, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(master=window)
        btn_frame.pack(side=tk.BOTTOM)

        clear_btn = tk.Button(master=btn_frame, text="Clear Data", command=self.clear_data)
        clear_btn.pack(side=tk.LEFT)

        time_range_btn = tk.Button(master=btn_frame, text="Set Time Range", command=self.set_time_range)
        time_range_btn.pack(side=tk.LEFT)

        self.df = pd.DataFrame()
        self.time_range = None
        self.filename = None

        self.client_names = [
            '20200118\\310',
            '20200118\\311',
            '20200118\\312',
            '20200119\\310',
            '20200119\\311',
            '20200119\\312',
            '20200120\\310',
            '20200120\\312',
            '20200121\\310',
            '20200121\\312'
        ]

        selected_client_var = tk.StringVar(self.window)
        selected_client_var.set(self.client_names[0])  # Set the default selected client

        utc_frame = tk.Frame(master=window)
        utc_frame.pack(side=tk.BOTTOM)

        self.utc_var = tk.BooleanVar()
        self.utc_checkbox = tk.Checkbutton(self.window, text="Display in UTC", variable=self.utc_var)
        self.utc_checkbox.pack()
        self.utc_var.trace('w', self.on_utc_changed)

        self.data_stream_names = ['Eda avg', 'Acc magnitude avg', 'Temp avg', 'Movement intensity', 'Steps count','Rest']
        selected_data_stream_var = tk.StringVar(self.window)
        selected_data_stream_var.set(self.data_stream_names[0])  # Set the default selected data stream

        self.selected_data_stream = self.data_stream_names[0]  # Initialize self.selected_data_stream

        def on_data_stream_selected(*args):
            self.selected_data_stream = selected_data_stream_var.get()  # Get the selected data stream
            self.plot_data()

        selected_data_stream_var.trace('w', on_data_stream_selected)

        self.data_stream_dropdown = tk.OptionMenu(self.window, selected_data_stream_var, *self.data_stream_names)
        self.data_stream_dropdown.pack(side=tk.RIGHT)

        def on_client_selected(*args):
            selected_client = selected_client_var.get()  # Get the selected client
            folder_path = os.path.join(os.getcwd(), 'Dataset', selected_client)
            file_path = os.path.join(folder_path, 'summary.csv')

            if os.path.exists(file_path):
                self.filename = file_path
                self.plot_data()
            else:
                messagebox.showerror("File Not Found", f"The file {file_path} does not exist.")

        selected_client_var.trace('w', on_client_selected)

        self.client_dropdown = tk.OptionMenu(self.window, selected_client_var, *self.client_names)
        self.client_dropdown.pack(side=tk.RIGHT)

        stats_btn = tk.Button(master=btn_frame, text="Show Statistics", command=self.show_stats)
        stats_btn.pack(side=tk.LEFT)

    # Defining the function on_utc_changed:
    def on_utc_changed(self, *args):
        self.plot_data()

    def format_time(self, x, pos=None):
        h = int(x % 60)
        m = int((x % 3600) // 60)
        s = int(x // 3600)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def clear_data(self):
        self.ax.clear()
        self.canvas.draw()
        self.df = pd.DataFrame()
        self.time_range = None
        self.selected_data_stream = None

    def set_time_range(self):
        try:
            start_str = simpledialog.askstring("Time Range", "Enter start time (HH:MM:SS):")
            end_str = simpledialog.askstring("Time Range", "Enter end time (HH:MM:SS):")
            start = datetime.strptime(start_str, "%H:%M:%S").time()
            end = datetime.strptime(end_str, "%H:%M:%S").time()

            start = timedelta(hours=start.hour, minutes=start.minute, seconds=start.second)
            end = timedelta(hours=end.hour, minutes=end.minute, seconds=end.second)

            if start is not None and end is not None and start < end:
                self.time_range = (start, end)
                self.plot_data()  # Replot data with the new time range
            else:
                messagebox.showerror("Invalid Time Range", "Start time must be less than end time.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Time inputs must be in HH:MM:SS format.")

    def show_stats(self):
        if self.df.empty:
            messagebox.showerror("No Data", "Please load data first.")
            return

        # Create a new window
        stats_window = tk.Toplevel(self.window)
        stats_window.title("Statistics")

        # Compute and display the basic statistics for the 'Acc magnitude avg' and 'Eda avg' columns
        for column in [self.selected_data_stream]:
            stats = self.df[column].describe()
            stats_str = f"{column}:\nMean: {stats['mean']}\nMedian: {self.df[column].median()}\nStd. dev: {stats['std']}\nMin: {stats['min']}\nMax: {stats['max']}"

            label = tk.Label(master=stats_window, text=stats_str, justify=tk.LEFT)
            label.pack()

    def plot_data(self):
        if self.filename is None:
            messagebox.showerror("No File Selected", "Please select a CSV file.")
            return

        if not os.path.isfile(self.filename):
            messagebox.showerror("File Not Found", f"The selected file '{self.filename}' does not exist.")
            return

        try:
            self.df = pd.read_csv(self.filename, usecols=self.data_stream_names + ['Unix Timestamp (UTC)'])
            self.df['Datetime'] = pd.to_datetime(self.df['Unix Timestamp (UTC)'], unit='ms')

            if self.utc_var.get():
                # Convert to UTC if necessary
                self.df['Datetime'] = self.df['Datetime'].dt.tz_localize('UTC')
            else:
                # Convert to local time if necessary
                local_tz = get_localzone()
                self.df['Datetime'] = self.df['Datetime'].dt.tz_localize('UTC').dt.tz_convert(local_tz)

            self.df['Minute'] = self.df['Datetime'].dt.minute + self.df['Datetime'].dt.hour * 60 + self.df[
                'Datetime'].dt.second / 60

            # Convert 'Minute' column to time format (hours:minutes:seconds)
            self.df['Minute'] = pd.to_timedelta(self.df['Minute'], unit='m')

            # Drop rows with missing data
            self.df.dropna(inplace=True)

            # Sort data by 'Minute' column
            self.df.sort_values('Minute', inplace=True)

            self.ax.clear()

            if self.time_range:
                start, end = self.time_range
                df_range = self.df[(self.df['Minute'] >= start) & (self.df['Minute'] <= end)]
            else:
                df_range = self.df

            self.ax.scatter(df_range['Minute'].dt.total_seconds() / 3600, df_range[self.selected_data_stream],
                         label=self.selected_data_stream, color='c')
            self.ax.set_title(f'{self.selected_data_stream} Over Time', fontweight='bold', color='m')
            self.ax.set_xlabel('Time (H:M:S)', fontweight='bold')
            self.ax.set_ylabel(self.selected_data_stream, fontweight='bold')
            self.ax.xaxis.set_major_formatter(self.format_time)
            self.ax.legend()

            self.canvas.draw()
        except pd.errors.EmptyDataError:
            messagebox.showerror("Empty File", "The selected file is empty.")
        except pd.errors.ParserError:
            messagebox.showerror("Invalid File", "The selected file is not a valid CSV file.")

            if self.utc_var.get():
                # Convert to UTC if necessary
                df_range['Time'] = df_range['Time'].apply(lambda x: x.to_pydatetime().replace(tzinfo=pytz.UTC))
            else:
                # Convert to local time if necessary
                df_range['Time'] = df_range['Time'].apply(
                    lambda x: x.to_pydatetime().replace(tzinfo=pytz.UTC).astimezone(tz=None))

if __name__ == "__main__":
    root = tk.Tk()
    DataVisualizer(root)
    root.mainloop()
