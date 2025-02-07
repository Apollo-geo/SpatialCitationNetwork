import os
import shutil
import xml.etree.ElementTree as ET
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['LiteratureNetwork']
collection = db['ORCID_above6kb']

#XML Parsing
def xml_to_dict(element):
    result = {}
    for child in element:
        if child.tag in result:
            if not isinstance(result[child.tag], list):
                result[child.tag] = [result[child.tag]]
            result[child.tag].append(xml_to_dict(child))
        else:
            result[child.tag] = xml_to_dict(child) if len(child) > 0 else child.text
    return result

# Base directory where the folders are located
base_dir = 'your_ORCID_data'

# Maximum allowed BSON size in bytes
max_bson_size = 16793598

overflow_folder_path = 'another_folder'

#Loop through folders named 000 to 999
for i in range(1000):
    folder_name = str(i).zfill(3)  # Convert integer to string and pad with zeros
    folder_path = os.path.join(base_dir, folder_name)

    # Check if the folder exists
    if os.path.exists(folder_path):
        # Loop through all files in the folder
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)

            # Check if the file size is within the BSON size limit
            if os.path.getsize(file_path) > max_bson_size:
                # Copy the file to another folder
                shutil.copy(file_path, os.path.join(overflow_folder_path, filename))
                print(f'{file_path} is too large to be inserted. Skipping.')
                continue

            # Loading XML
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Convert data structure
            data = xml_to_dict(root)

            # Insert data
            collection.insert_one(data)

            # Process the content as needed
            print(f'{file_path} has been imported.')
    
    else:
        print(f'Folder {folder_path} does not exist.')
