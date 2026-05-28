import os
import zipfile
import csv
from datetime import datetime
from math import radians, cos, sin, sqrt, atan2

# # Directory containing the input ZIP files
# zip_dir = 'AIS_2016_January'

# # Directory to save extracted CSV files
# raw_ais_csv = 'AIS_2016_January_Processed'

# Directory containing the input ZIP files
# zip_dir = r"D:\Temp\AIS\AIS_Data\AIS_2024_RAW"

# Directory to save extracted CSV files
raw_ais_csv = r"D:\Temp\AIS\AIS_Data\AIS_2025_RAW"

# Create the extraction directory if it doesn't exist
if not os.path.exists(raw_ais_csv):
    os.makedirs(raw_ais_csv)

# Two adjacent points of the same vessel within this threshold will be removed
threshold_in_meters = 100
## changed to 100 meters from 30 meters on 2025-11-03 to eliminate crashes

# def process_csv(csv_path):
#     output_csv_path = os.path.join(os.path.dirname(csv_path), f'Filtered_{os.path.basename(csv_path)}')
    
#     with open(csv_path, 'r', newline='') as csvfile, open(output_csv_path, 'w', newline='') as filtered_csvfile:
#         reader = csv.reader(csvfile)
#         writer = csv.writer(filtered_csvfile)
        
#         header = next(reader)  # Read the header
#         writer.writerow(header)  # Write the header to the filtered CSV
        
#         # Example: Filter rows and write to the filtered CSV
#         for row in reader:
#             writer.writerow(row)

# Function to calculate the distance between two points using the Haversine formula
def haversine(lat1, lon1, lat2, lon2):
    R = 6371e3  # Radius of the Earth in meters
    phi1 = radians(lat1)
    phi2 = radians(lat2)
    delta_phi = radians(lat2 - lat1)
    delta_lambda = radians(lon2 - lon1)

    a = sin(delta_phi / 2.0) ** 2 + cos(phi1) * cos(phi2) * sin(delta_lambda / 2.0) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c

# Clean up the input csv data and remove rows with bad values
def cleanupData(data):
    cleaned_data = []
    skipped_count = 0

    for i, row in enumerate(data):
        try:
            base_datetime = row.get('base_date_time', '')

            # Check if the base_datetime value is in the correct format before attempting to parse it
            # Handle both 'T' and space separator formats
            if len(base_datetime) == 19 and base_datetime[4] == '-' and base_datetime[7] == '-':
                if base_datetime[10] == 'T':
                    # Format: 2025-01-01T00:00:00
                    row['base_date_time'] = datetime.strptime(base_datetime, '%Y-%m-%dT%H:%M:%S')
                elif base_datetime[10] == ' ':
                    # Format: 2025-01-01 00:00:00
                    row['base_date_time'] = datetime.strptime(base_datetime, '%Y-%m-%d %H:%M:%S')
                else:
                    skipped_count += 1
                    if skipped_count <= 5:
                        print(f"Skipped row {i}: Invalid datetime separator: '{base_datetime}'")
                    continue
                    
                row['latitude'] = float(row['latitude'])
                row['longitude'] = float(row['longitude'])
                cleaned_data.append(row)  # Add row to data list if parsing is successful
            else:
                skipped_count += 1
                if skipped_count <= 5:  # Show first few skipped rows for debugging
                    print(f"Skipped row {i}: Invalid datetime format: '{base_datetime}'")
                # Skip rows where 'base_date_time' doesn't match the expected format
                continue
        except (ValueError, KeyError) as e:
            skipped_count += 1
            if skipped_count <= 5:  # Show first few errors for debugging
                print(f"Skipped row {i}: {e} - Row: {row}")
            # Skip rows with invalid values
            continue
    
    print(f"Skipped {skipped_count} rows during cleanup")
    return cleaned_data

def removeRedundancies(csv_path):
    print(f"Processing file: {csv_path}")
    
    with open(csv_path) as file:
        reader = csv.DictReader(file)
        data = list(reader)
        
        print(f"Total rows read: {len(data)}")
        if data:
            print(f"First row keys: {list(data[0].keys())}")
            print(f"First row sample: {data[0]}")
        
        # Extract field names from the input CSV
        fieldnames = reader.fieldnames
        print(f"Field names: {fieldnames}")
        
        cleaned_data = cleanupData(data)
        print(f"Rows after cleanup: {len(cleaned_data)}")
        
        if not cleaned_data:
            print("WARNING: No data remaining after cleanup!")
            return

        # # Convert 'base_date_time' to datetime object for accurate sorting
        # for row in data:
        #     row['base_date_time'] = datetime.strptime(row['base_date_time'], '%Y-%m-%dT%H:%M:%S')  # Adjust format as needed
        #     row['LAT'] = float(row['LAT'])
        #     row['LON'] = float(row['LON'])

        # Sort data by 'mmsi' and 'base_date_time'
        sorted_data = sorted(cleaned_data, key=lambda row: (row['mmsi'], row['base_date_time']))
        print(f"Rows after sorting: {len(sorted_data)}")

        filtered_data = []
        last_seen = {}
        
        for row in sorted_data:
            mmsi = row['mmsi']
            lat = row['latitude']
            lon = row['longitude']

            if mmsi not in last_seen:
                filtered_data.append(row)
                last_seen[mmsi] = (lat, lon)
            else:
                last_lat, last_lon = last_seen[mmsi]
                distance = haversine(last_lat, last_lon, lat, lon)
                
                if distance >= threshold_in_meters:
                    filtered_data.append(row)
                    last_seen[mmsi] = (lat, lon)

        print(f"Final filtered rows: {len(filtered_data)}")
        
        if not filtered_data:
            print("WARNING: No data remaining after filtering!")
            return

        # for row in filtered_data:
        #     # Convert 'base_date_time' back to string for printing
        #     row['base_date_time'] = row['base_date_time'].strftime('%Y-%m-%dT%H:%M:%S')
        #     print(row)
        #     # Write the filtered data to a new CSV file

    output_csv_path = os.path.join(raw_ais_csv, f'Filtered_{threshold_in_meters}m_{os.path.basename(csv_path)}')

    with open(output_csv_path, 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in filtered_data:
            # Convert 'base_date_time' back to string for writing (use original format with space)
            row['base_date_time'] = row['base_date_time'].strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow(row)

    file.close()
    outfile.close()

# Iterate through all ZIP files in the directory
print(f"Looking for CSV files in directory: {raw_ais_csv}")
files_in_dir = os.listdir(raw_ais_csv)
print(f"Files found: {files_in_dir}")

for file_name in files_in_dir:
    # if file_name.endswith('.zip'):
    #     zip_path = os.path.join(zip_dir, file_name)
    #     csv_name = file_name.replace('.zip', '.csv')
    #     extract_path = os.path.join(raw_ais_csv, csv_name)
        
    #     # Unzip the file
    #     with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    #         zip_ref.extractall(raw_ais_csv)
        
    #     # Check if the extracted CSV exists and process it
    #     csv_path = os.path.join(raw_ais_csv, csv_name)
    #     if os.path.exists(csv_path):
    if file_name.endswith('.csv'):
        csv_path = os.path.join(raw_ais_csv, file_name)   
        removeRedundancies(csv_path)
        print(f'Processed: {file_name}')
    else:
        print(f'CSV file not found: {file_name}')