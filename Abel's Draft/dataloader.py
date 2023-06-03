import os
import pandas as pd


class DataLoader():
    def getData(self):
        data_folder = 'Dataset'

        # List of all the date folders
        date_folders = ['20200118', '20200119', '20200120', '20200121']  # January 18th-21st, 2020

        # List of all the subfolders within the date folders
        subfolders = ['310', '311', '312']

        # Initialize empty lists to store the file paths
        metadata_files = []
        summary_files = []

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
                        metadata_files.append(metadata_file_path)

                    # Check if the summary.csv file exists
                    if os.path.isfile(summary_file_path):
                        summary_files.append(summary_file_path)

        # Load the metadata files into a DataFrame
        metadata_dataframes = [pd.read_csv(file) for file in metadata_files]

        # Load the summary files into a DataFrame
        summary_dataframes = [pd.read_csv(file) for file in summary_files]

        return metadata_dataframes,summary_dataframes


