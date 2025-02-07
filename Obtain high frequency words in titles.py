from pymongo import MongoClient
from datetime import datetime
from collections import Counter
import re
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['LiteratureNetwork']
collection = db['Papers']
references_collection = db['References']

# Example: Extract documents from 2019
start = datetime(2022, 12, 31)
end = datetime(2023, 6, 30)
titles = collection.find({
    'Create Date': {'$gte': start, '$lte': end}
}, {'Title': 1})

def word_freq(titles):
    counter = Counter()
    for title in titles:
        words = re.findall(r'\w+', title['Title'].lower())  # Extract words and convert to lowercase
        counter.update(words)
    return counter.most_common(50)  # Get the 10 most frequent words

freq = word_freq(titles)

# Assume freq_2019 is the data for 2019, and so on
# You need to replace the results of each time period here
data = {
    'Term': [term for term, count in freq],
    'Frequency': [count for term, count in freq],
}

df= pd.DataFrame(data)
# Repeat the above process to generate more DataFrames

# Save all DataFrames to different sheets in the same Excel file
with pd.ExcelWriter('word_frequency2023f.xlsx') as writer:
    df.to_excel(writer, sheet_name='2023f', index=False)
    # Repeat this step to save data for other years

# Close the database connection
client.close()