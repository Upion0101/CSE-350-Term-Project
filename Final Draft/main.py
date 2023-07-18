import tkinter as tk
import pypyodbc as odbc
from credential import username, password
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
from tkinter import filedialog, simpledialog, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import style
import pandas as pd
import os
import pytz
from datetime import datetime, timedelta
from tzlocal import get_localzone

style.use("seaborn-darkgrid")
style.use("dark_background")


class DataVisualizer:

    def __init__(self, window):

        self.df = pd.DataFrame()
        self.timeRange = None
        self.filename = None

        self.clientNames = [
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

        # Create window
        self.window = window
        self.window.title("RogerWare Prototype")

        # Edit canvas
        self.fig = Figure(figsize=(10, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        """Buttons and Dropdown menus"""
        btnFrame = tk.Frame(master=window)
        btnFrame.pack(side=tk.BOTTOM)

        # Change between utc and local time button
        utcFrame = tk.Frame(master=window)
        utcFrame.pack(side=tk.BOTTOM)

        # Clear button
        clearBtn = tk.Button(master=btnFrame, text="Clear Data", command=self.clearData)
        clearBtn.pack(side=tk.LEFT)

        # Time range button
        timeRangeBtn = tk.Button(master=btnFrame, text="Enter Time Range", command=self.setTimeRange)
        timeRangeBtn.pack(side=tk.LEFT)

        # Statistical Analysis Button
        statsBtn = tk.Button(master=btnFrame, text="Statistical Analysis", command=self.statsAnalysis)
        statsBtn.pack(side=tk.LEFT)

        # Connect Database button
        connectDbBtn = tk.Button(master=btnFrame, text="Connect to Database", command=self.connectDb)
        connectDbBtn.pack(side=tk.RIGHT)

        # Query button
        queryDbBtn = tk.Button(master=btnFrame, text="Query", command=self.onQuerySelect)
        queryDbBtn.pack(side=tk.RIGHT)

        # Connect Database button
        uploadCSVBtn = tk.Button(master=btnFrame, text="Upload CSV", command=self.onUploadCSVSelect)
        uploadCSVBtn.pack(side=tk.RIGHT)

        selectedClientVar = tk.StringVar(self.window)
        selectedClientVar.set(self.clientNames[0])  # Set the default selected client

        # Dropdown for graph type selection
        self.graphTypes = ['Line', 'Bar', 'Scatter plot']
        selectedGraphTypeVar = tk.StringVar(self.window)
        selectedGraphTypeVar.set(self.graphTypes[0])  # Set the default graph type to 'Line'
        self.selectedGraphType = self.graphTypes[0]  # Initialize self.selectedGraphType

        graphTypeDropdown = tk.OptionMenu(self.window, selectedGraphTypeVar, *self.graphTypes,
                                          command=self.onGraphTypeSelected)
        graphTypeDropdown.pack()

        # Dropdown for data stream selection
        self.dataStreamNames = ['Eda avg', 'Acc magnitude avg', 'Temp avg', 'Movement intensity', 'Steps count',
                                'Rest', 'On Wrist']
        selectedDataStreamVar = tk.StringVar(self.window)
        selectedDataStreamVar.set(self.dataStreamNames[0])  # Set the default selected data stream
        self.selectedDataStream = self.dataStreamNames[0]  # Initialize self.selectedDataStream

        # Boolean for UTC checkbox
        self.utcVar = tk.BooleanVar()
        self.utcCheckbox = tk.Checkbutton(self.window, text="Convert to UTC", variable=self.utcVar)
        self.utcCheckbox.pack()
        self.utcVar.trace('w', self.onUtcChanged)

        """Buttons and Dropdown menus end here"""




        #### Function definitions ###

        def onDataStreamSelected(*args):
            self.selectedDataStream = selectedDataStreamVar.get()  # Get the selected data stream
            self.plotData()

        selectedDataStreamVar.trace('w', onDataStreamSelected)

        self.dataStreamDropdown = tk.OptionMenu(self.window, selectedDataStreamVar, *self.dataStreamNames)
        self.dataStreamDropdown.pack()

        def onClientSelected(*args):
            selectedClient = selectedClientVar.get()  # Get the selected client
            folderPath = os.path.join(os.getcwd(), 'Dataset', selectedClient)
            filePath = os.path.join(folderPath, 'summary.csv')

            if os.path.exists(filePath):
                self.filename = filePath
                self.plotData()
            else:
                messagebox.showerror("File Not Found", f"The file {filePath} does not exist.")

        selectedClientVar.trace('w', onClientSelected)

        self.clientDropdown = tk.OptionMenu(self.window, selectedClientVar, *self.clientNames)
        self.clientDropdown.pack()

    def onUtcChanged(self, *args):
        self.plotData()

    def formatTime(self, x, pos=None):
        h = int(x)
        m = int((x * 60) % 60)
        s = int((x * 3600) % 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def onGraphTypeSelected(self, selectedGraphType):
        self.selectedGraphType = selectedGraphType
        self.plotData()

    def clearData(self):
        self.ax.clear()
        self.canvas.draw()
        self.df = pd.DataFrame()
        self.timeRange = None

    @staticmethod
    def connectDb():
        server = 'cse535.database.windows.net'
        database = 'ProjectDB'
        driver = '{ODBC Driver 18 for SQL Server}'
        connectionString = odbc.connect(
            'DRIVER=' + driver + ';SERVER=tcp:' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
        print(connectionString)
    def onQuerySelect(self):
        return
    def onUploadCSVSelect(self):
        return

    def setTimeRange(self):
        try:
            startStr = simpledialog.askstring("Time Range", "Enter start time (HH:MM:SS):")
            endStr = simpledialog.askstring("Time Range", "Enter end time (HH:MM:SS):")
            # For whatever reason, time was being read backward, so adjustment was made for user's convenience
            start = datetime.strptime(startStr, "%H:%M:%S").time()
            end = datetime.strptime(endStr, "%H:%M:%S").time()

            start = timedelta(hours=start.hour, minutes=start.minute, seconds=start.second)
            end = timedelta(hours=end.hour, minutes=end.minute, seconds=end.second)

            # Plot data with the new time range
            if start is not None and end is not None and start < end:
                self.timeRange = (start, end)
                self.plotData()
            else:
                messagebox.showerror("Invalid Time Range", "Start time must be less than end time.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Time inputs must be in HH:MM:SS format.")

    def statsAnalysis(self):
        if self.df.empty:
            messagebox.showerror("No Data", "Please load data first.")
            return

        # Create a new window
        statsWindow = tk.Toplevel(self.window)
        statsWindow.title("Statistical Analysis")

        # Compute and display the basic statistics for the columns
        for column in [self.selectedDataStream]:
            stats = self.df[column].describe()
            statsStr = f"{column}:\nMean: {stats['mean']}\nMedian: {self.df[column].median()}\nStd. dev: {stats['std']}\nMin: {stats['min']}\nMax: {stats['max']}"

            label = tk.Label(master=statsWindow, text=statsStr, justify=tk.LEFT)
            label.pack()

    def plotData(self):
        if self.filename is None:
            messagebox.showerror("No File Selected", "Please select a CSV file.")
            return

        if not os.path.isfile(self.filename):
            messagebox.showerror("File Not Found", f"The selected file '{self.filename}' does not exist.")
            return

        try:
            self.df = pd.read_csv(self.filename, usecols=self.dataStreamNames + ['Unix Timestamp (UTC)'])
            self.df['Datetime'] = pd.to_datetime(self.df['Unix Timestamp (UTC)'], unit='ms')

            if self.utcVar.get():
                # Convert to UTC if necessary
                self.df['Datetime'] = self.df['Datetime'].dt.tz_localize('UTC')
            else:
                # Convert to local time if necessary
                localTz = get_localzone()
                self.df['Datetime'] = self.df['Datetime'].dt.tz_localize('UTC').dt.tz_convert(localTz)

            self.df['Minute'] = self.df['Datetime'].dt.minute + self.df['Datetime'].dt.hour * 60 + self.df[
                'Datetime'].dt.second / 60

            # Convert 'Minute' column to hours:minutes:seconds format
            self.df['Minute'] = pd.to_timedelta(self.df['Minute'], unit='m')

            # Drop rows with missing data
            self.df.dropna(inplace=True)

            # Sort data by 'Minute' column
            self.df.sort_values('Minute', inplace=True)

            self.ax.clear()

            if self.timeRange:
                start, end = self.timeRange
                dfRange = self.df[(self.df['Minute'] >= start) & (self.df['Minute'] <= end)]
            else:
                dfRange = self.df

            xValues = dfRange['Minute'].dt.total_seconds() / 3600
            yValues = dfRange[self.selectedDataStream]

            if self.selectedGraphType == 'Line':
                self.ax.plot(xValues, yValues, label=self.selectedDataStream, color='plum')
            elif self.selectedGraphType == 'Bar':
                self.ax.bar(xValues, yValues, label=self.selectedDataStream, color='plum')
            elif self.selectedGraphType == 'Scatter plot':
                self.ax.scatter(xValues, yValues, label=self.selectedDataStream, color='plum')

            self.ax.set_title(f'{self.selectedDataStream} Over Time', fontweight='bold', color='cornflowerblue')
            self.ax.set_xlabel('Time', fontweight='bold', color='cornflowerblue')
            self.ax.set_ylabel(self.selectedDataStream, fontweight='bold', color='cornflowerblue')
            self.ax.xaxis.set_major_formatter(self.formatTime)

            self.ax.legend()
            self.canvas.draw()

        except pd.errors.EmptyDataError:
            messagebox.showerror("Empty File", "File is empty.")
        except pd.errors.ParserError:
            messagebox.showerror("Invalid File", "File is not a valid CSV file.")


if __name__ == "__main__":
    root = tk.Tk()
    dataVisualizer = DataVisualizer(root)
    root.mainloop()