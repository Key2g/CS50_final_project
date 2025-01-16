import sqlite3
import csv
import os
from tkinter import filedialog
import tkinter as tk
from configuration import Config

def export_to_csv(database_name:str, table_name:str, default_path:str = None):
    # Get the default path from config if not provided
    if default_path is None:
        config = Config()
        default_path = config.get("export_filepath", "")

    # Create a root window and hide it
    root = tk.Tk()
    root.withdraw()

    # Open file dialog to choose save path and filename
    output_name = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        title="Save CSV file as",
        initialdir=default_path
    )

    # If user cancels the file dialog, exit the function
    if not output_name:
        print("Export cancelled.")
        return

    # Connect to the database
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    # Query to fetch all data from the table
    query = f"SELECT * FROM {table_name}"
    cursor.execute(query)

    # Fetch column names
    column_names = [description[0] for description in cursor.description]

    # Open a CSV file to write data
    with open(output_name, "w", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)

        # Write the column names as the first row
        csv_writer.writerow(column_names)

        # Write all rows from the database table
        csv_writer.writerows(cursor.fetchall())

    # Close the database connection
    conn.close()

    print(f"Export complete! File saved as: {output_name}")


def insert_data_to_db(database_name:str, table_name:str, date: str, t1: float, t2: float, t3: float):
    # Connect to the database and insert data (avoids accidental UI variable polluting the DB)
    conn = sqlite3.connect(database_name)
    query = f"""
    INSERT INTO {table_name} (data, t1, t2, t3)
    VALUES (?, ?, ?, ?)
    """
    cursor = conn.cursor()
    cursor.execute(query, (date, t1, t2, t3))
    conn.commit()
    conn.close()
    print(f"Data inserted into the database: {date, t1, t2, t3}")
    
def fetch_last_n_records(database, table_name, n):
    # Fetch the last n records from the database table order by id.
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    
    # Query to get the first and last dates of the last n records
    query = f"""
    SELECT MIN(data), MAX(data)
    FROM (
        SELECT data
        FROM {table_name}
        ORDER BY id DESC
        LIMIT {n}
    )
    """
    
    cursor.execute(query)
    first_date, last_date = cursor.fetchone()
    
    conn.close()
    
    return first_date, last_date
    
def records_by_time_csv(database_name, table_name, start_date, end_date, default_path: str = None):
    try:
        # Get the default path from config if not provided
        if default_path is None:
            config = Config()
            default_path = config.get("export_filepath", "")

        # Create a root window and hide it
        root = tk.Tk()
        root.withdraw()

        # Open file dialog to choose save path and filename
        output_name = filedialog.asksaveasfilename(
            initialfile= f"1wire_{start_date.strftime("%Y%m%d_%H%M%S")}_{end_date.strftime("%Y%m%d_%H%M%S")}.csv",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save CSV file as",
            initialdir=default_path
        )

        # If user cancels the file dialog, exit the function
        if not output_name:
            print("Export cancelled.")
            return
        # Connect to the database
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()

        # Query to fetch data between the specified dates
        query = f"""
        SELECT data, T1, T2, T3, comment 
        FROM {table_name} 
        WHERE data BETWEEN ? AND ?
        ORDER BY data;
        """
        cursor.execute(query, (start_date, end_date))

        # Fetch column names and rows
        column_names = [description[0] for description in cursor.description]
        rows = cursor.fetchall()

        # Open a CSV file to write data
        with open(output_name, "w", newline="", encoding="utf-8") as csv_file:
            csv_writer = csv.writer(csv_file)

            # Write the column names as the header
            csv_writer.writerow(column_names)

            # Write sanitized rows to the CSV
            csv_writer.writerows(rows)

        # Close the database connection
        conn.close()

        print(f"Export complete! File saved as: {output_name}")
    except Exception as e:
        print(f"An error occurred: {e}")


def fetch_filtered_data(db_path, table_name, start_time, end_time):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = f"""
    SELECT id, data, CAST(T1 AS FLOAT), CAST(T2 AS FLOAT), CAST(T3 AS FLOAT), 
           CAST((T1 + T2 + T3) / 3.0 AS FLOAT) as avg_temp,
           comment
    FROM {table_name}
    WHERE data BETWEEN ? AND ?
    ORDER BY data
    """
    cursor.execute(query, (start_time.strftime("%Y-%m-%d %H:%M:%S"), end_time.strftime("%Y-%m-%d %H:%M:%S")))
    data = cursor.fetchall()
    conn.close()
    return data

def add_comment(database_name, table_name, timestamp:str, comment:str):
    try:
        if len(comment)>250:
            print("Comment is too long. Maximum length is 250 characters.")
            return
        
        # Connect to the database
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()
        # Update the comment in the database
        query = f"UPDATE {table_name} SET comment = ? WHERE data = ?"
        cursor.execute(query, (comment, timestamp))
        conn.commit()
        print("Comment updated successfully.")
        conn.close()
        
    except Exception as e:
        print(f"An error occurred while updating comment: {e}")
        
def create_db(database_name:str, table_name:str):
    try:
        # Connect to the database
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()
        
        # Create the table if it doesn't exist
        query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data DATETIME DEFAULT CURRENT_TIMESTAMP,
            T1 FLOAT(10,2),
            T2 FLOAT(10,2),
            T3 FLOAT(10,2),
            comment VARCHAR(250) DEFAULT ''
        );
        """
        cursor.execute(query)
        conn.commit()
        print("Table created successfully.")
        conn.close()
    
    except Exception as e:
        print(f"An error occurred while creating table: {e}")
        
def get_date_range(database_name: str, table_name: str):
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    query = f"SELECT MIN(data), MAX(data) FROM {table_name}"
    cursor.execute(query)
    min_date, max_date = cursor.fetchone()
    conn.close()
    if min_date is None or max_date is None:
        print("No data found in the table.")
        return None, None
    min_date = min_date.split('.')[0]
    max_date = max_date.split('.')[0]
    print(f"Data range: {min_date} to {max_date}")
    return min_date, max_date

