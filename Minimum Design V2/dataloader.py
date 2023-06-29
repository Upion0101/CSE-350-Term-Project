import os
import pandas as pd


class DataLoader():
    client_names = [
        '20200118/310',
        '20200118/311',
        '20200118/312',
        '20200119/310',
        '20200119/311',
        '20200119/312',
        '20200120/310',
        '20200120/312',
        '20200121/310',
        '20200121/312'
    ]
    def read_csv(self):
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
        metadata_df = [pd.read_csv(file) for file in metadata_files]
        # Load the summary files into a DataFrame
        summary_df = [pd.read_csv(file) for file in summary_files]


        return metadata_df,summary_df

    def get_specific_client(self, client):
        metadata_df, summary_df = self.read_csv()

        if client in self.client_names:
            client_metadata = None
            client_summary = None

            # Find the specific client's metadata and summary dataframes
            for df in metadata_df:
                if client in df['Client'].values:
                    client_metadata = df
                    break

            for df in summary_df:
                if client in df['Client'].values:
                    client_summary = df
                    break

            return client_metadata, client_summary
        else:
            return None, None

# Example usage
data_loader = DataLoader()
client = '20200118/310'
metadata, summary = data_loader.get_specific_client(client)
if metadata is not None and summary is not None:
    print(f"Metadata for client '{client}':")
    print(metadata)

    print(f"\nSummary for client '{client}':")
    print(summary)
else:
    print(f"No data found for client '{client}'.")



