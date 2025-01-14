import tkinter as tk
from tkinter import simpledialog, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import style
import pandas as pd
import os
from datetime import datetime, timedelta
from tzlocal import get_localzone

style.use("seaborn-darkgrid")
style.use("dark_background")


class DataVisualizer:

    def __init__(self, window):
        # Create window
        self.window = window
        self.window.title("RogerWare Prototype")

        # Edit canvas
        self.fig = Figure(figsize=(10, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(master=window)
        btn_frame.pack(side=tk.BOTTOM)

        # Clear button
        clear_btn = tk.Button(master=btn_frame, text="Clear Data", command=self.clear_data)
        clear_btn.pack(side=tk.LEFT)

        # Time range button
        time_range_btn = tk.Button(master=btn_frame, text="Enter Time Range", command=self.set_time_range)
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

        # Boolean for UTC checkbox
        self.utc_var = tk.BooleanVar()
        self.utc_checkbox = tk.Checkbutton(self.window, text="Convert to UTC", variable=self.utc_var)
        self.utc_checkbox.pack()
        self.utc_var.trace('w', self.on_utc_changed)

        # Dropdown for data stream selection
        self.data_stream_names = ['Eda avg', 'Acc magnitude avg', 'Temp avg', 'Movement intensity', 'Steps count', 'Rest', 'On Wrist']
        selected_data_stream_var = tk.StringVar(self.window)
        selected_data_stream_var.set(self.data_stream_names[0])  # Set the default selected data stream

        self.selected_data_stream = self.data_stream_names[0]  # Initialize self.selected_data_stream

        # Dropdown for graph type selection
        self.graph_types = ['Line', 'Bar', 'Scatter plot']
        selected_graph_type_var = tk.StringVar(self.window)
        selected_graph_type_var.set(self.graph_types[0])  # Set the default graph type to 'Line'
        self.selected_graph_type = self.graph_types[0]  # Initialize self.selected_graph_type

        graph_type_dropdown = tk.OptionMenu(self.window, selected_graph_type_var, *self.graph_types,command=self.on_graph_type_selected)
        graph_type_dropdown.pack()

        # Function definitions

        def on_data_stream_selected(*args):
            self.selected_data_stream = selected_data_stream_var.get()  # Get the selected data stream
            self.plot_data()

        selected_data_stream_var.trace('w', on_data_stream_selected)

        self.data_stream_dropdown = tk.OptionMenu(self.window, selected_data_stream_var, *self.data_stream_names)
        self.data_stream_dropdown.pack()

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
        self.client_dropdown.pack()

        stats_btn = tk.Button(master=btn_frame, text="Statistical Analysis", command=self.stats_analysis)
        stats_btn.pack(side=tk.LEFT)

    def on_utc_changed(self, *args):
        self.plot_data()
    def format_time(self, x, pos=None):
        h = int(x // 3600)
        m = int((x % 3600) // 60)
        s = int(x % 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def on_graph_type_selected(self, selected_graph_type):
        self.selected_graph_type = selected_graph_type
        self.plot_data()

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
            # For whatever reason, time was being read backward, so adjustment was made for user's convenience
            start = datetime.strptime(start_str, "%H:%M:%S").time()
            end = datetime.strptime(end_str, "%H:%M:%S").time()

            start = timedelta(hours=start.hour, minutes=start.minute, seconds=start.second)
            end = timedelta(hours=end.hour, minutes=end.minute, seconds=end.second)

            # Plot data with the new time range
            if start is not None and end is not None and start < end:
                self.time_range = (start, end)
                self.plot_data()
            else:
                messagebox.showerror("Invalid Time Range", "Start time must be less than end time.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Time inputs must be in HH:MM:SS format.")

    def stats_analysis(self):
        if self.df.empty:
            messagebox.showerror("No Data", "Please load data first.")
            return

        # Create a new window
        stats_window = tk.Toplevel(self.window)
        stats_window.title("Statistical Analysis")

        # Compute and display the basic statistics for the columns
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

            # read CSV and convert to UTC or local time
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

            # Convert 'Minute' column to hours:minutes:seconds format
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

            # X and Y values to plot specified graph type
            x_values = df_range['Minute'].dt.total_seconds() / 3600
            y_values = df_range[self.selected_data_stream]

            if self.selected_graph_type == 'Line':
                self.ax.plot(x_values, y_values, label=self.selected_data_stream, color='plum')
            elif self.selected_graph_type == 'Bar':
                self.ax.bar(x_values, y_values, label=self.selected_data_stream, color='plum')
            elif self.selected_graph_type == 'Scatter plot':
                self.ax.scatter(x_values, y_values, label=self.selected_data_stream, color='plum')

            self.ax.set_title(f'{self.selected_data_stream} Over Time', fontweight='bold', color='cornflowerblue')
            self.ax.set_xlabel('Time', fontweight='bold', color='cornflowerblue')
            self.ax.set_ylabel(self.selected_data_stream, fontweight='bold', color='cornflowerblue')
            self.ax.xaxis.set_major_formatter(self.format_time)

            self.ax.legend()
            self.canvas.draw()

        except pd.errors.EmptyDataError:
            messagebox.showerror("Empty File", "File is empty.")
        except pd.errors.ParserError:
            messagebox.showerror("Invalid File", "File is not a valid CSV file.")


if __name__ == "__main__":
    root = tk.Tk()
    DataVisualizer(root)
    root.mainloop()