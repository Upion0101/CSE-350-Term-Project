import tkinter as tk
from data_visualizer import DataVisualizer
from data_loader import DataLoader

# Create the main application window
root = tk.Tk()

# Initialize the data visualizer and data loader
data_visualizer = DataVisualizer(root)
data_loader = DataLoader(data_visualizer)

# Create the menu bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# Create the "File" menu
file_menu = tk.Menu(menu_bar, tearoff=False)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Load Data", command=data_loader.load_data)

# Run the application
root.mainloop()