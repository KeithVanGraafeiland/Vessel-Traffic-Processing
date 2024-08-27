import os
import zipfile
import csv
from datetime import datetime
from math import radians, cos, sin, sqrt, atan2


# Directory containing the input ZIP files
zip_dir = r"E:\AIS\MarineCadastre\2023"

# Directory to save extracted CSV files
extract_dir = r"E:\AIS\MarineCadastre\2023\processed"

# Two adjacent points of the same vessel within this threshold will be removed
threshold_in_meters = 30

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

    for row in data:
        base_datetime = row.get('BaseDateTime', '')

        # Check if the base_datetime value is in the correct format before attempting to parse it
        if len(base_datetime) == 19 and base_datetime[4] == '-' and base_datetime[7] == '-' and base_datetime[10] == 'T':
            try:
                # Attempt to parse the 'BaseDateTime' field
                row['BaseDateTime'] = datetime.strptime(base_datetime, '%Y-%m-%dT%H:%M:%S')
                row['LAT'] = float(row['LAT'])
                row['LON'] = float(row['LON'])
                cleaned_data.append(row)  # Add row to data list if parsing is successful
            except ValueError:
                print(row)
                # Skip rows with invalid 'BaseDateTime' values
                continue
        else:
            # Skip rows where 'BaseDateTime' doesn't match the expected format
            continue

    return cleaned_data

def removeRedundencies(csv_path):
    with open(csv_path) as file:
        reader = csv.DictReader(file)
        data = cleanupData(list(reader))

        # Extract field names from the input CSV
        fieldnames = reader.fieldnames

        # # Convert 'BaseDateTime' to datetime object for accurate sorting
        # for row in data:
        #     row['BaseDateTime'] = datetime.strptime(row['BaseDateTime'], '%Y-%m-%dT%H:%M:%S')  # Adjust format as needed
        #     row['LAT'] = float(row['LAT'])
        #     row['LON'] = float(row['LON'])

        # Sort data by 'MMSI' and 'BaseDateTime'
        sorted_data = sorted(data, key=lambda row: (row['MMSI'], row['BaseDateTime']))

        filtered_data = []
        last_seen = {}
        
        for row in sorted_data:
            mmsi = row['MMSI']
            lat = row['LAT']
            lon = row['LON']

            if mmsi not in last_seen:
                filtered_data.append(row)
                last_seen[mmsi] = (lat, lon)
            else:
                last_lat, last_lon = last_seen[mmsi]
                distance = haversine(last_lat, last_lon, lat, lon)
                
                if distance >= threshold_in_meters:
                    filtered_data.append(row)
                    last_seen[mmsi] = (lat, lon)

        # for row in filtered_data:
        #     # Convert 'BaseDateTime' back to string for printing
        #     row['BaseDateTime'] = row['BaseDateTime'].strftime('%Y-%m-%dT%H:%M:%S')
        #     print(row)
        #     # Write the filtered data to a new CSV file

    output_csv_path = os.path.join(os.path.dirname(csv_path), f'Filtered_{os.path.basename(csv_path)}')

    with open(output_csv_path, 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in filtered_data:
            # Convert 'BaseDateTime' back to string for writing
            row['BaseDateTime'] = row['BaseDateTime'].strftime('%Y-%m-%dT%H:%M:%S')
            writer.writerow(row)

    file.close()
    outfile.close()

# Iterate through all ZIP files in the directory
for file_name in os.listdir(zip_dir):
    if file_name.endswith('.zip'):
        zip_path = os.path.join(zip_dir, file_name)
        csv_name = file_name.replace('.zip', '.csv')
        extract_path = os.path.join(extract_dir, csv_name)
        
        # Unzip the file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Check if the extracted CSV exists and process it
        csv_path = os.path.join(extract_dir, csv_name)
        if os.path.exists(csv_path):
            removeRedundencies(csv_path)

            print(f'Processed: {csv_name}')
        else:
            print(f'CSV file not found: {csv_name}')