import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import style
import pandas as pd
import os

# Apply custom style
style.use('ggplot')

class DataVisualizer:

    def __init__(self, window):
        self.window = window
        self.window.title("Data Visualizer")

        self.fig = Figure(figsize=(5, 5), dpi=100)
        self.axes = self.fig.subplots(2, 1)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(master=window)
        btn_frame.pack(side=tk.BOTTOM)

        clear_btn = tk.Button(master=btn_frame, text="Clear Data", command=self.clear_data)
        clear_btn.pack(side=tk.LEFT)

        time_range_btn = tk.Button(master=btn_frame, text="Set Time Range", command=self.set_time_range)
        time_range_btn.pack(side=tk.LEFT)

        data_stream_1_btn = tk.Button(master=btn_frame, text="Set Data Stream", command=self.set_time_range)
        data_stream_1_btn.pack(side=tk.RIGHT)

        data_stream_2_btn = tk.Button(master=btn_frame, text="Set Data Stream", command=self.set_time_range)
        data_stream_2_btn.pack(side=tk.RIGHT)

        change_time = tk.Button(master=btn_frame, text="Set Data Stream", command=self.set_time_range)
        data_stream_2_btn.pack(side=tk.RIGHT)


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

        stats_btn = tk.Button(master=btn_frame, text="Show Statistics", command=self.show_stats)
        stats_btn.pack(side=tk.LEFT)

        self.plot_data()

    def clear_data(self):
        for ax in self.axes:
            ax.clear()
        self.canvas.draw()
        self.df = pd.DataFrame()
        self.time_range = None
        self.filename = None

    def set_time_range(self):
        try:
            start = simpledialog.askfloat("Time Range", "Enter start time:")
            end = simpledialog.askfloat("Time Range", "Enter end time:")
            if start is not None and end is not None and start < end:
                self.time_range = (start, end)
                self.plot_data()  # Replot data with the new time range
            else:
                messagebox.showerror("Invalid Time Range", "Start time must be less than end time.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Time inputs must be numeric.")

    def show_stats(self):
        if self.df.empty:
            messagebox.showerror("No Data", "Please load data first.")
            return

        # Create a new window
        stats_window = tk.Toplevel(self.window)
        stats_window.title("Statistics")

        # Compute and display the basic statistics for the 'Acc magnitude avg' and 'Eda avg' columns
        for column in ['Acc magnitude avg', 'Eda avg']:
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
            self.df = pd.read_csv(self.filename, usecols=['Eda avg', 'Acc magnitude avg', 'Unix Timestamp (UTC)'])
            self.df['Datetime'] = pd.to_datetime(self.df['Unix Timestamp (UTC)'], unit='ms')
            self.df['Minute'] = self.df['Datetime'].dt.minute + self.df['Datetime'].dt.hour * 60

            # Drop rows with missing data
            self.df.dropna(inplace=True)

            # Sort data by 'Minute' column
            self.df.sort_values('Minute', inplace=True)

            for ax in self.axes:
                ax.clear()

            if self.time_range:
                start, end = self.time_range
                df_range = self.df[(self.df['Minute'] >= start) & (self.df['Minute'] <= end)]
            else:
                df_range = self.df

            self.axes[0].plot(df_range['Minute'], df_range['Acc magnitude avg'], label='Acc magnitude avg', color='c')
            self.axes[0].set_title('Acc magnitude avg Over Time', fontweight='bold', color='m')
            self.axes[0].set_xlabel('Time (minutes)', fontweight='bold')
            self.axes[0].set_ylabel('Acc magnitude avg', fontweight='bold')
            self.axes[0].legend()

            self.axes[1].plot(df_range['Minute'], df_range['Eda avg'], label='Eda avg', color='b')
            self.axes[1].set_title('Eda avg Over Time', fontweight='bold', color='m')
            self.axes[1].set_xlabel('Time (minutes)', fontweight='bold')
            self.axes[1].set_ylabel('Eda avg', fontweight='bold')
            self.axes[1].legend()

            # Adjust the spacing between subplots
            self.fig.subplots_adjust(hspace=0.5)

            self.canvas.draw()
        except pd.errors.EmptyDataError:
            messagebox.showerror("Empty File", "The selected file is empty.")
        except pd.errors.ParserError:
            messagebox.showerror("Invalid File", "The selected file is not a valid CSV file.")


if __name__ == "__main__":
    root = tk.Tk()
    DataVisualizer(root)
    root.mainloop()