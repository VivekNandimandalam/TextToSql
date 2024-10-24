import os
import time
import pandas as pd

# Folder where new files will arrive
folder_to_watch = r'C:\Users\Vivek.Nandimandalam\OneDrive - DISYS\Project K\Excel Files'  # Use raw string
master_file_path = r'C:\Users\Vivek.Nandimandalam\OneDrive - DISYS\Project K\Master data folder\Master Data File.xlsx'  # Use raw string

# Function to append new data to the master file
def append_to_master(new_file):
    # Load the master file
    master_df = pd.read_excel(master_file_path)
    
    # Load the new file data
    new_data_df = pd.read_excel(new_file)
    
    # Append the new data to the master data
    updated_master_df = pd.concat([master_df, new_data_df], ignore_index=True)
    
    # Save the updated master file
    updated_master_df.to_excel(master_file_path, index=False)
    print(f"Appended data from {new_file} to {master_file_path}")

# Monitor the folder for new files
processed_files = set()

while True:
    # Get the list of files in the directory
    files_in_directory = set(os.listdir(folder_to_watch))
    
    # Identify new files that haven't been processed yet
    new_files = files_in_directory - processed_files
    
    # Process new files that start with 'dummy_cost_data'
    for new_file in new_files:
        if new_file.startswith('dummy_cost_data') and new_file.endswith('.xlsx'):
            file_path = os.path.join(folder_to_watch, new_file)
            append_to_master(file_path)
            processed_files.add(new_file)  # Mark file as processed
    
    # Wait before checking again (e.g., every 10 seconds)
    time.sleep(10)
