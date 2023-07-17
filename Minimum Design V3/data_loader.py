import tkinter.filedialog as filedialog
from tkinter import messagebox
import os
import pandas as pd


class DataLoader:
    def __init__(self, visualizer):
        self.visualizer = visualizer

    def load_data(self):
        folder_path = filedialog.askdirectory(title="Select Folder")
        if folder_path:
            try:
                summary_file_path = os.path.join(folder_path, 'summary.csv')
                if os.path.isfile(summary_file_path):
                    self.visualizer.filename = summary_file_path
                    self.visualizer.plot_data()
                else:
                    messagebox.showerror("File Not Found", f"The file 'summary.csv' does not exist in the selected folder.")
            except pd.errors.ParserError:
                messagebox.showerror("Invalid File", "The selected file is not a valid CSV file.")
        else:
            messagebox.showinfo("Folder Selection", "No folder selected.")