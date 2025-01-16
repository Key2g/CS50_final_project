
# Wire Reader App

## Project Overview

Wire Reader App is a Python-based application developed for monitoring a bio-reactor at Wrocław University of Environmental and Life Sciences. This software provides real-time temperature monitoring, data logging, and visualization capabilities for RapsberryPi 1-Wire temperature sensors.

For more info check out WireReaderApp User Manual.

## Features

- Real-time temperature monitoring from three sensors
- Live graphical representation of temperature data
- Data logging to SQLite database
- CSV export functionality for logged data
- Configurable settings through a user interface
- Debug mode for testing without physical sensors

## Requirements

- Python 3.x
- Required Python packages:
  - numpy
  - pandas
  - matplotlib
  - tkcalendar

## Installation

1. Clone the repository:
    `git clone https://github.com/Key2dev/1wire_revised.git`
    `cd 1wire_revised`

2. Install the required packages:
    `pip install -r requirements.txt`

## Usage

1. Run the main application:
    `python wire_reader_app.py`

2. The application window will open, displaying real-time temperature readings and a live graph.

3. Use the buttons in the interface to:

- Export the database to a CSV file
- Filter and view specific data ranges
- Configure application settings
- Toggle data recording on/off

## Filter

The Filter functionality allows users to view and analyze specific ranges of data:

1. Click the "Filter" button in the main interface to open the submenu.
2. In the submenu, you can:
   - Select a date range for filtering data
   - Visualize filtered data in a graph
   - Save data between specified range
   - Visualize last n number of records

### Graph Visualization

- The graph displays temperature data for all three sensors over the selected time range.
- You can zoom in/out and pan the graph for detailed analysis.
- Hover over data points to see exact temperature and timestamp values.
- Use checkboxes for selective display of sensors

### Data Interaction

- Click on a row in the data table to add or edit comments for specific data points.
- Use the "Update Comment" button to save your changes.

### Saving Filtered Data

1. After applying your desired filter, use the "Save Filtered Data" button.
2. Choose a location and filename for your CSV file.
3. The filtered data, including timestamps, temperature readings, and comments, will be saved to the CSV file.

This feature is particularly useful for:

- Analyzing specific time periods
- Exporting subsets of data for further analysis in other tools
- Adding and preserving notes about particular events or observations

## Configuration

- The application uses a `config.json` file for storing configuration settings.
- You can modify these settings through the "Config" button in the application UI.
- Key configurable parameters include:
  - Database path
  - Table name
  - Update interval (in miliseconds)
  - Number of graph points to display on live graph in the main window
  - Debug mode - (!!important info!!) to start the app for the first time in debug mode change `config.json`

## Development

- The project is structured with separate modules for different functionalities:
  - `main.py`: Main application logic and UI
  - `db_functions.py`: Database operations
  - `wire_reader.py`: Sensor reading functionality
  - `configuration.py`: Configuration management
  - `submenu.py`: Submenu for data filtering
  - `debug_functions.py`: Debug utilities

## Contributing

Contributions to the 1Wire Revised project are welcome. Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is licensed under MIT License. See the LICENSE file for details.

## Contact

For any queries regarding this project, please contact Key2dev at <kkolodynski.dev@gmail.com>.
