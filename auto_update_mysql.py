import os
import time
import pandas as pd
import mysql.connector

# MySQL connection details
MYSQL_HOST = 'localhost'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'admin'
MYSQL_DATABASE = 'Master Data Mysql'

# Folder where Master Data File is located
master_file_path = r'C:\Users\Vivek.Nandimandalam\OneDrive - DISYS\Project K\Master data folder\Master Data File.xlsx'

# Function to create a MySQL connection
def get_mysql_connection():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD
    )

# Function to ensure database exists
def ensure_database_exists():
    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DATABASE}`")
    conn.close()

# Function to create or update the table in MySQL
def update_mysql_table(dataframe):
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )
    
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS `excel_data` (
        `Resource` VARCHAR(255),
        `ResourceId` VARCHAR(255),
        `ResourceType` VARCHAR(255),
        `ResourceGroupName` VARCHAR(255),
        `ResourceGroupId` VARCHAR(255),
        `ResourceLocation` VARCHAR(255),
        `SubscriptionName` VARCHAR(255),
        `SubscriptionId` VARCHAR(255),
        `ServiceName` VARCHAR(255),
        `ServiceTier` VARCHAR(255),
        `Meter` VARCHAR(255),
        `PartNumber` VARCHAR(255),
        `Cost` DECIMAL(10, 2),
        `CostUSD` DECIMAL(10, 2),
        `Currency` VARCHAR(255)
    )
    """)
    
    # Insert the DataFrame into the MySQL table
    for _, row in dataframe.iterrows():
        cursor.execute("""
        INSERT INTO `excel_data` (`Resource`, `ResourceId`, `ResourceType`, `ResourceGroupName`, 
        `ResourceGroupId`, `ResourceLocation`, `SubscriptionName`, `SubscriptionId`, `ServiceName`, 
        `ServiceTier`, `Meter`, `PartNumber`, `Cost`, `CostUSD`, `Currency`)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, tuple(row))
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Updated MySQL table with {len(dataframe)} records.")

# Monitor the master file for changes and update MySQL
def monitor_and_update_mysql():
    last_modified_time = None
    
    while True:
        current_modified_time = os.path.getmtime(master_file_path)
        
        if last_modified_time is None or current_modified_time != last_modified_time:
            print("Detected update in Master Data File.xlsx.")
            
            # Read the updated Excel file
            df = pd.read_excel(master_file_path)
            
            # Ensure the MySQL database exists
            ensure_database_exists()
            
            # Update the MySQL table with the data
            update_mysql_table(df)
            
            last_modified_time = current_modified_time
        
        # Wait for a while before checking again (e.g., every 10 seconds)
        time.sleep(10)

# Start monitoring
if __name__ == "__main__":
    monitor_and_update_mysql()
