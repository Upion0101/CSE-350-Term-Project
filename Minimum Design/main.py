import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import style
import pandas as pd

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

        load_btn = tk.Button(master=btn_frame, text="Load CSV", command=self.load_csv)
        load_btn.pack(side=tk.LEFT)

        clear_btn = tk.Button(master=btn_frame, text="Clear Data", command=self.clear_data)
        clear_btn.pack(side=tk.LEFT)

        time_range_btn = tk.Button(master=btn_frame, text="Set Time Range", command=self.set_time_range)
        time_range_btn.pack(side=tk.LEFT)

        self.df = pd.DataFrame()
        self.time_range = None
        self.filename = None

        stats_btn = tk.Button(master=btn_frame, text="Show Statistics", command=self.show_stats)
        stats_btn.pack(side=tk.LEFT)

    def load_csv(self):
        filename = filedialog.askopenfilename(filetypes=[('CSV Files', '*.csv')])
        if filename:
            self.filename = filename  # Store filename for later use
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


if __name__ == "__main__":
    root = tk.Tk()
    DataVisualizer(root)
    root.mainloop()