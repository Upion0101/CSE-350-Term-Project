import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

class DataLoader:
    def __init__(self):
        self.metadata_files = []
        self.summary_files = []
        self.sensor_data = pd.DataFrame()

    def readCSV(self):
        data_folder = 'Dataset'

        # List of all the date folders
        date_folders = ['20200118', '20200119', '20200120', '20200121']  # January 18th-21st, 2020

        # List of all the subfolders within the date folders
        subfolders = ['310', '311', '312']

        # Loop through the date folders and subfolders
        for date_folder in date_folders:
            for subfolder in subfolders:
                folder_path = os.path.join(data_folder, date_folder, subfolder)

                # Check if the folder exists
                if os.path.exists(folder_path):
                    metadata_file_path = os.path.join(folder_path, 'metadata.csv')
                    summary_file_path = os.path.join(folder_path, 'summary.csv')

                    # Check if the metadata.csv file exists
                    if os.path.isfile(metadata_file_path):
                        self.metadata_files.append(metadata_file_path)

                    # Check if the summary.csv file exists
                    if os.path.isfile(summary_file_path):
                        self.summary_files.append(summary_file_path)

        # Load the metadata files into a DataFrame
        metadata_df = [pd.read_csv(file) for file in self.metadata_files]

        # Load the summary files into a DataFrame
        summary_df = [pd.read_csv(file) for file in self.summary_files]

        # Merge the metadata and summary DataFrames
        self.sensor_data = pd.concat(metadata_df + summary_df)

    def getParticipants(self):
        # Get unique participants from the loaded sensor data
        participants = self.sensor_data['Participant'].unique().tolist()
        return participants

    def getDataStreams(self, participant):
        # Get available data streams for a specific participant
        participant_data = self.sensor_data[self.sensor_data['Participant'] == participant]
        data_streams = participant_data.columns.tolist()
        return data_streams

    def getParticipantData(self, participant, data_streams):
        # Get sensor data for the specified participant and data streams
        participant_data = self.sensor_data[self.sensor_data['Participant'] == participant]
        selected_data = participant_data[data_streams]
        return selected_data

class VisualPanel:
    def __init__(self):
        self.time_series = []
        self.chart_type = "line"

    def setTimeSeries(self, time_series):
        self.time_series = time_series

    def setChartType(self, chart_type):
        self.chart_type = chart_type

    def displayChart(self):
        # Display the time series data using the specified chart type
        if self.chart_type == "line":
            plt.plot(self.time_series)
        elif self.chart_type == "scatter":
            plt.scatter(range(len(self.time_series)), self.time_series)
        # Add more chart types as needed

        plt.xlabel("Time")
        plt.ylabel("Data Value")
        plt.title("Sensor Data Visualization")
        plt.show()

class TimeConverter:
    def __init__(self):
        self.timezone = "UTC"

    def convertToTimezone(self, timestamp):
        # Convert timestamp to the specified timezone (UTC or local time)
        if self.timezone == "local":
            # Perform timezone conversion using appropriate libraries or functions
            pass
        return timestamp

class DataExplorer:
    def __init__(self, data_loader, visual_panel, time_converter):
        self.data_loader = data_loader
        self.visual_panel = visual_panel
        self.time_converter = time_converter

    def exploreData(self, participant, data_streams):
        # Get the sensor data for the specified participant and data streams
        participant_data = self.data_loader.getParticipantData(participant, data_streams)

        # Convert timestamps to the desired timezone
        participant_data['Timestamp'] = participant_data['Timestamp'].apply(self.time_converter.convertToTimezone)

        # Synchronize the time series across data streams
        synchronized_data = participant_data[data_streams].copy()

        # Display the synchronized time series using the visual panel
        self.visual_panel.setTimeSeries(synchronized_data)
        self.visual_panel.displayChart()

# Create instances of the required classes
data_loader = DataLoader()
visual_panel = VisualPanel()
time_converter = TimeConverter()
data_explorer = DataExplorer(data_loader, visual_panel, time_converter)

# Read the CSV files and load the sensor data
data_loader.readCSV()

# Get participants and data streams
participants = data_loader.getParticipants()
data_streams = data_loader.getDataStreams(participants[0])  # Select the first participant

# Explore data for the first participant and data streams
data_explorer.exploreData(participants[0], data_streams)