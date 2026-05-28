import os
import requests
from bs4 import BeautifulSoup
import zipfile

# Directory containing the zip files
directory = r'C:\AIS_ZIP\2024'

# URL to check for updates
url = 'https://coast.noaa.gov/htdata/CMSP/AISDataHandler/2024/index.html'

# Get the list of existing zip files in the directory
existing_files = set(os.listdir(directory))

# Fetch the HTML content from the URL
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Find all links to zip files
zip_links = soup.find_all('a', href=True)
for link in zip_links:
    href = link['href']
    if href.endswith('.zip'):
        zip_file_name = href.split('/')[-1]
        zip_path = os.path.join(directory, zip_file_name)
        if zip_file_name not in existing_files:
            # Download the missing or updated zip file
            zip_url = url.rsplit('/', 1)[0] + '/' + href
            zip_response = requests.get(zip_url)
            with open(zip_path, 'wb') as f:
                f.write(zip_response.content)
            print(f'Downloaded: {zip_file_name}')
        else:
            print(f'Already exists: {zip_file_name}')
        # Extract the downloaded zip file
        extract_directory = r'C:\AIS\AIS_2024'
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_directory)
        print(f'Extracted: {zip_file_name} to {extract_directory}')