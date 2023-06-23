# Imports
from dataloader import DataLoader

# instantiate classes
dataLoader = DataLoader()

# switch print debug on and off
DEBUG = True

metadata_dataframes, summary_dataframes = dataLoader.readCSV()


# Debugging prints
if DEBUG == True:
    # Print the loaded dataframes
    print("Metadata DataFrames:")
    for df in metadata_dataframes:
        print(df)

    print("Summary DataFrames:")
    for df in summary_dataframes:
        print(df)
