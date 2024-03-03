
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import pandas as pd
import requests
import os 
import re
from typing import List

import sys 
sys.path.append("../src")


def find_hrefs(url):
    """Find all hrefs available in a page"""
    try:
        # Fetch the HTML content of the webpage
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all href attributes in the <a> tags
        hrefs = [a.get('href') for a in soup.find_all('a', href=True)]

        return hrefs

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the page: {e}")
        return []
    

# # Example usage:
# xml_file = 'example.xml'  # Replace with the path to your XML file
# result = xml_to_dict(xml_file)


def join_csv_files(input_directory, output_file=None):
    """Join all csv file found in a directory.
    """

    # Check if the input directory exists
    if not os.path.exists(input_directory):
        print(f"Error: The directory '{input_directory}' does not exist.")
        return

    # Get a list of all CSV files in the input directory
    files = os.listdir(input_directory)
    df = pd.concat([pd.read_csv(os.path.join(input_directory, file)) for file in files])
    
    # Write the combined DataFrame to a new CSV file
    if output_file:
        df.to_csv(output_file, index=False)
        print(f"Combined data written to '{output_file}'.")
    else:
        return df


def get_dataframe_size(df):
    # Get memory usage of each column in bytes
    memory_usage_per_column = df.memory_usage(deep=True)

    # Calculate total memory usage in bytes
    total_memory_usage = memory_usage_per_column.sum()

    # Convert bytes to gigabytes
    total_memory_usage_gb = total_memory_usage / (1024 ** 3)

    return total_memory_usage_gb



def split_text_into_chunks(text, max_tokens):
    """
    Split a given text into chunks of manageable size based on the maximum number of tokens.
    Splitting at punctuation and concatenating sentences if their total length is less than max tokens.

    Parameters:
    - text (str): The input text to be split.
    - max_tokens (int): The maximum number of tokens allowed per chunk.

    Returns:
    - List[str]: A list of text chunks.
    """
    # Split the text into sentences using regex
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        sentence_tokens = len(sentence.split())
        if len(current_chunk.split()) + sentence_tokens <= max_tokens:
            current_chunk += " " + sentence if current_chunk else sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def count_tokens(text):
    # Split the text into words and count the number of words
    words = text.split()
    num_tokens = len(words)
    return num_tokens


def group_documents(documents, token_limit):
    """Group contents by cutting at token limit
    
    Arguments:
        documents: list
        token_limit: int
    """

    chunks = []
    temp_chunk = ''

    # Remove any non string item
    documents = list(filter(lambda x: isinstance(x, str), documents))

    for idx, document in enumerate(documents):

        if count_tokens(document) < token_limit:
            
            if count_tokens(temp_chunk + document) < token_limit:
                temp_chunk += document

                if idx+1 == len(documents):
                    chunks.append(temp_chunk)
            else:
                chunks.append(temp_chunk)
                print("Created chunk")
                temp_chunk = document
        else:
            print("""Single speech larger than token limit, 
                consider increasing limit or splitting""")
            continue

    print(f"Split the speeches in {len(chunks)}")
    
    return chunks