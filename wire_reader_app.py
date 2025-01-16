from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from collections import deque
import tkinter as tk
import debug_functions as debugf
import db_functions
import datetime
from submenu import Submenu
from configuration import Config
import sys

# Old reader implementation
from wire_reader import read_1wire_sensors

class WireReaderApp:
    def __init__(self):
        """
        Initialize the WireReaderApp.

        This method sets up the main window, initializes variables for data storage and display,
        creates UI elements including labels and buttons, and sets up a live graph for temperature visualization.
        """

        # Create a new Toplevel window
        self.root = tk.Tk()
        self.root.title("Wire Reader App")

        # Load configuration
        self.config = Config(self.root)
        
        # Database Variables
        self.db_path = self.config.get("db_path")
        self.table_name = self.config.get("table_name")

        # Data Variables
        self.data_time = ""
        self.data_temp1 = 0.0
        self.data_temp2 = 0.0
        self.data_temp3 = 0.0

        # Bool for stopping the update loop
        self.inserting_data = False
        
        # Store historical data for the graph
        self.max_points = self.config.get("graph_points")
        
        self.temps1 = deque(maxlen=self.max_points)
        self.temps2 = deque(maxlen=self.max_points)
        self.temps3 = deque(maxlen=self.max_points)

        # Label Variables for UI
        self.time_now = tk.StringVar()
        self.temp1 = tk.StringVar()
        self.temp2 = tk.StringVar()
        self.temp3 = tk.StringVar()
        
        # Create status indicators
        self.create_status_indicators()

        # Create UI elements (labels, buttons, etc.)
        self.create_ui_elements()
        
        # Check database connection
        self.check_db_connection()

        # Live Graph
        self.create_live_graph()

        # Start updating the GUI
        self.update_all()

    def create_ui_elements(self):
        # Create a frame for data labels
        data_frame = tk.Frame(self.root, relief=tk.RAISED, borderwidth=1)
        data_frame.pack(padx=10, pady=10, fill=tk.X)

        # Time label
        time_frame = tk.Frame(data_frame, relief=tk.SUNKEN, borderwidth=1)
        time_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(time_frame, text="Date:", font=('Arial', '12', 'bold')).pack(side=tk.LEFT, padx=5)
        tk.Label(time_frame, textvariable=self.time_now, font=('Arial', '12')).pack(side=tk.RIGHT, padx=5)

        # Temperature labels
        temp_frame = tk.Frame(data_frame, relief=tk.SUNKEN, borderwidth=1)
        temp_frame.pack(fill=tk.X, padx=5, pady=5)

        for i, temp_var in enumerate([self.temp1, self.temp2, self.temp3], start=1):
            tk.Label(temp_frame, text=f"Temp {i}:", font=('Arial', '12', 'bold')).pack(side=tk.LEFT, padx=5)
            tk.Label(temp_frame, textvariable=temp_var, font=('Arial', '12')).pack(side=tk.LEFT, padx=5)
            
        # Add average temperature label
        self.avg_temp = tk.StringVar()
        avg_temp_frame = tk.Frame(self.root, relief=tk.RAISED, borderwidth=1)
        avg_temp_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(avg_temp_frame, text="Average Temperature:", font=('Arial', '14', 'bold')).pack(side=tk.LEFT, padx=5)
        tk.Label(avg_temp_frame, textvariable=self.avg_temp, font=('Arial', '14', 'bold'), fg='blue').pack(side=tk.LEFT, padx=5)

        # Button frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        # Toggle data recording button
        self.toggle_insertion_button = tk.Button(self.root, text="Toggle data recording", font=('Arial', '12'), command=self.toggle_insertion)
        self.toggle_insertion_button.pack(padx=10, pady=10)
        # Buttons
        buttons = [
            ("Export DB", self.export_db),
            ("Filter", self.open_submenu),
            ("Config", self.configuration_menu),
            ("Exit", self.exit_click)
        ]

        for text, command in buttons:
            tk.Button(button_frame, text=text, font=('Arial', '12'), command=command, width=20).pack(pady=5)

        self.root.protocol("WM_DELETE_WINDOW", self.exit_click)

        
    def create_status_indicators(self):
        status_frame = tk.Frame(self.root)
        status_frame.pack(fill="x", padx=10, pady=5)
    
        self.app_status = tk.Label(status_frame, text="App: Running", bg="green", fg="white", padx=5, pady=2)
        self.app_status.pack(side="left", padx=5)
    
        self.db_status = tk.Label(status_frame, text="DB: Connected", bg="green", fg="white", padx=5, pady=2)
        self.db_status.pack(side="left", padx=5)
    
        self.data_status = tk.Label(status_frame, text="Data: Not Recording", bg="red", fg="white", padx=5, pady=2)
        self.data_status.pack(side="left", padx=5)
    
    def create_live_graph(self):
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.line, = self.ax.plot([], [], label="Temp1")
        self.line2, = self.ax.plot([], [], label="Temp2", color='r')
        self.line3, = self.ax.plot([], [], label="Temp3", color='g')
        temp_range = self.config.get("temperature_range")
        self.ax.set_ylim(temp_range[0], temp_range[1])
        self.ax.legend()
        self.ax.set_title("Live Temperature Plot")
        self.ax.set_xlabel(f"Last {self.max_points} records")
        self.ax.set_ylabel("Temperature (°C)")

        # Embed Matplotlib Figure in Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(padx=10, pady=10)

    def update_all(self):
        self.update_variables()
        if self.inserting_data:
            db_functions.insert_data_to_db(self.db_path, self.table_name, self.data_time, self.data_temp1, self.data_temp2, self.data_temp3)
        self.update_labels()
        self.update_graph()
        self.update_job = self.root.after(self.config.get("update_interval"), self.update_all)

    def update_variables(self):
        self.data_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self.config.get("debug_mode"):
            self.data_temp1 = debugf.random_temp()
            self.data_temp2 = debugf.random_temp()
            self.data_temp3 = debugf.random_temp()
        else:
            temps = read_1wire_sensors()
            self.data_temp1 = temps[0]
            self.data_temp2 = temps[1]
            self.data_temp3 = temps[2]
        
        self.temps1.append(self.data_temp1)
        self.temps2.append(self.data_temp2)
        self.temps3.append(self.data_temp3)
        
    def update_labels(self):
        # Update label variables with data values
        self.time_now.set(f"{self.data_time}")
        self.temp1.set(f"{self.data_temp1}")
        self.temp2.set(f"{self.data_temp2}")
        self.temp3.set(f"{self.data_temp3}")
        
        # Calculate and update average temperature
        avg_temp = (self.data_temp1 + self.data_temp2 + self.data_temp3) / 3
        self.avg_temp.set(f"{avg_temp:.2f} °C")

    def update_graph(self):
        # Plot temperature data vs index (just using len() for index)
        indices = list(range(len(self.temps1)))  # Create a simple index list for x-axis this is 'time'

        # Set data for each plot
        self.line.set_data(indices, self.temps1)  # Temp1 plot
        self.line2.set_data(indices, self.temps2)  # Temp2 plot
        self.line3.set_data(indices, self.temps3)  # Temp3 plot

        # Adjust the x-axis to display a limited number of recent data points
        self.ax.set_xlim(0, len(self.temps1) + 1)  # Show all available data points, +1 is for slight lead in graph

        # Update x-axis ticks and labels (using the index as labels)
        self.ax.xaxis.set_major_locator(plt.MultipleLocator(10))  # Major ticks every 10 data points
        self.ax.xaxis.set_minor_locator(plt.MultipleLocator(5))   # Minor ticks every 5 data points
        self.ax.set_xlabel(f"Last {self.max_points} records")

        self.canvas.draw()

    def export_db(self):
        print("Export DataBase to csv file")
        db_functions.export_to_csv(self.db_path, self.table_name, self.config.get("export_path"))

        
    def open_submenu(self):
        # Implement a submenu for filtering data
        print("Opening Filter Submenu")
        
        Submenu(self.root)
        
    def toggle_insertion(self):
        self.inserting_data = not self.inserting_data
        if self.inserting_data:
            self.toggle_insertion_button.config(text="Stop Recording Data")
            self.data_status.config(text="Data: Recording", bg="green")
            print("Data insertion started")
        else:
            self.toggle_insertion_button.config(text="Start Recording Data")
            self.data_status.config(text="Data: Not Recording", bg="red")
            print("Data insertion stopped")

    def check_db_connection(self):
        try:
            db_functions.create_db(self.db_path, self.table_name)
            self.db_status.config(text="DB: Connected", bg="green")
        except Exception as e:
            print(f"Database connection error: {e}")
            self.db_status.config(text="DB: Error", bg="red")

    def exit_click(self):
        if hasattr(self, '_exiting'):
            return  # Prevent multiple calls to exit_click
        self._exiting = True
        
        print("Exit clicked. Closing the application...")
        if hasattr(self, 'update_job'):
            self.root.after_cancel(self.update_job)
        
        # Save configuration before closing
        self.config.save_config()
        
        self.root.quit()
        self.root.destroy()
        
    def close_application(self):
        print("Closing application...")
        self.app_status.config(text="App: Closing", bg="red")
        # Cancel any scheduled after callbacks
        if hasattr(self, 'update_job'):
            self.root.after_cancel(self.update_job)  # Cancel the scheduled update

        # Close all top-level windows
        for window in self.root.winfo_children():
            if isinstance(window, tk.Toplevel):
                window.destroy()

        # Close the matplotlib figure
        plt.close(self.fig)

        # Destroy all widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Stop the main loop and destroy the root window
        self.root.quit()
        self.root.destroy()

        # Force exit the Python interpreter
        sys.exit(0)

        self.root.quit()  # Stop the main loop
        self.root.destroy()  # Free resources

    
    def configuration_menu(self):
        self.config.edit_config_ui()

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.close_application)
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.close_application()

def main():
    app = WireReaderApp()
    try:
        app.run()
    except Exception as e:
        print(f"An unhandled exception occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
