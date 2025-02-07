import requests
import xml.etree.ElementTree as ET
import csv
import re
import html
import csv
import time
import json

# Initialize an empty list to hold the data of the first column
PMID = []

with open('relevant papers.csv', 'r', encoding='utf-8') as csvfile:
    # Create a CSV reader object
    csvreader = csv.reader(csvfile)
    # Skip the header row (if any)
    header = next(csvreader)
    
    # Iterate through each line of the CSV file
    for row in csvreader:
        # row is a list, the first element is the value of the first column
        PMID.append(row[0])


api_key = "api_key_PubMed" # Replace with your API key
fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
info_lists = []
i=7601

for id in PMID[7600:]:
    time.sleep(0.3)  # Pause for 0.1 seconds
    # Construct API Request
    params = {
        "db": "pubmed",
        "id": id,
        "retmode": "xml",
        "api_key": api_key
    }
    response = requests.get(fetch_url, params=params)

    if response.status_code == 200:
        # Use regular expressions to extract the content of all <Citation> tags
        response_text = html.unescape(response.text)
        citations = re.findall('<Citation>(.*?)</Citation>', response_text, re.DOTALL)
        ArticleTitle = re.findall('<ArticleTitle>(.*?)</ArticleTitle>', response_text, re.DOTALL)
    else:
        print("Failed to retrieve data of"+id)

    # Initialize an empty list to hold all dictionaries
    citation_list = []
    info_list = []

    # Process each citation
    for citation in citations:
        parts = [part.strip() for part in citation.split('. ') if part.strip()]  # 分割字符串，并移除空白

        # Create a dictionary and assign values
        citation_dict = {}

        # Depending on the number of contents after "." segmentation, there may be different situations
        if len(parts) >= 3:
            citation_dict['Authors'] = parts[0]
            citation_dict['Title'] = parts[1]
            citation_dict['Details'] = parts[2]

        # Check if 'Title' contains any letters
        if 'Title' in citation_dict and not any(c.isalpha() for c in citation_dict['Title']):
            continue # If not included, skip this citation

        citation_list.append(citation_dict)
        info_list = ArticleTitle + citation_list

# Initialize an empty list to hold all citation_lists
    print(i)
    info_lists.append(info_list)
    if i % 100 == 0 or i == 7651:  # If i is a multiple of 100
    # Save the nested list as a JSON file
        with open(f'info_lists{i}.json', 'w', encoding='utf-8') as f:
            json.dump(info_lists, f, ensure_ascii=False, indent=4)
        info_lists.clear()
    i=i+1

