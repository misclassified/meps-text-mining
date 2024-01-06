from collections import namedtuple

import argparse
from bs4 import BeautifulSoup
import re
import requests
import time
import os
import logging
import yaml

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys 
sys.path.append("../src")
from utils import find_hrefs, join_csv_files
    

def fetch_results(html):
    """Fetch all a tags from an html page"""
    
    # Create a BeautifulSoup object
    soup = BeautifulSoup(html, 'html.parser')

    # Extract information
    a_tag = soup.find_all('a', class_='t-y')
    print(len(a_tag))

    results = []

    for tag in a_tag:
    
        name = tag.find('span', class_='t-item').text
        href = tag['href']
        res = (name, href)
        results.append(res)

    return results


def count_a_tags(page_source_html):
    """Utility function to count all the a tags in a source
    html page"""

    soup = BeautifulSoup(page_source_html, 'html.parser')
    a_tag = soup.find_all('a', class_='t-y')
    
    return len(a_tag)


def extract_content_from_url(url, verbose = False):
    """Extract all the class contents from an html 
    page and concatenate in a single text"""

    try:
        # Send an HTTP GET request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all elements with the class "content"
            content_elements = soup.find_all(class_="contents")

            # Extract and print the content

            concatenated_text = ""

            for element in content_elements:
                if verbose:
                    print(element.text)
                concatenated_text += element.text + "\n"

            return concatenated_text

        else:
            print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")



def find_date_from_url(url_string):
    """For url that contain a date looks for a data
    in yyyy-mm-dd format"""

    split_string = url_string.split("/")
    input_string = split_string[-1]

    # Define a regular expression pattern to match the date
    pattern = r'-(\d{4}-\d{2}-\d{2})'
    match = re.search(pattern, input_string)

    if match:
        # Extract the date and language code from the match
        date = match.group(1)
    else:
        print("No match found for Date")

    return date


def find_language_from_url(url_string):
    """Looks for a language reference in a 
    url and extracts it"""

    split_string = url_string.split("/")
    input_string = split_string[-1]

    pattern_lan = r'([A-Z]{2})\.html'
    match = re.search(pattern_lan, input_string)

    if match:
        # Extract the date and language code from the match
        lan = match.group(1)
    else:
        print("No match found for Language")

    return lan



def scrape_speeches(meps, europal_website, href_root, output_dir):
    """For each MEP of a set of MEPS find 
    all plenary interventions and scrape them
    
    Args:
        meps: pandas DataFrame. You should get this from 
                scrape_list_of_meps.py. Expect the following schema
                fullName -> str
                country -> str
                politicalGroup -> str
                id -> int
                nationalPoliticalGroup -> str
        europal_website: str
            root url of european parliament
        href_root: str
            europarl root path to build path to plenary speeches
        output_dir: str
            local path to save scraped data.
    """

    for mep in meps.itertuples():

        time.sleep(5)

        name = mep.fullName
        id = mep.id
        mep_href = os.path.join(href_root, str(id))
        outpath = os.path.join(output_dir, f"{name}.csv")
        print(f"Start Processing {name}")
        logging.info(f"--------------- Start Processing {name}")

        # Check if a file with the same name exist already


        # Find all page hrefs
        hrefs = find_hrefs(mep_href)
        try:
            temp_href = list(filter(lambda x: x.find('plenary-speeches') != -1, hrefs))[0]
        except IndexError:
            logging.info(f"There's no plenary-speeches for {name}")
            continue

        if temp_href is not None:
            target_href = europal_website + temp_href
            logging.info(f"Target Href for plenary debates {target_href}")
        else:
            print("I couldn't find a valid href")


        # Inizialize Web Drive and get page 
        driver = webdriver.Chrome()
        driver.get(target_href)


        # Agree on cookies to allow further action
        time.sleep(5)
        try:
            cookie_button = driver.find_element(By.CLASS_NAME, 'epjs_agree')
            actions = ActionChains(driver)
            actions.move_to_element(cookie_button).click().perform()
        except:
            pass

        # Find all the interventions made by MP
        # load_more_button = driver.find_element(By.CLASS_NAME, 'europarl-expandable-async-loadmore')
        # actions = ActionChains(driver)

        cnt = 0 

        print(f'Starting fetching list of speeches for {name}')
        logging.info(f'Starting fetching list of speeches for {name}')

        for i in range(100): #max 1000 plenary speeches interventions
            
            time.sleep(3)

            try:
                actions = ActionChains(driver)
                load_more_button = driver.find_element(By.CLASS_NAME, 'europarl-expandable-async-loadmore')
                if load_more_button.is_displayed():

                    cnt += 1
                    actions.move_to_element(load_more_button).click().perform()
                    logging.info(f'Iteration : {cnt} for {name}')
                    logging.info(f'Found {count_a_tags(driver.page_source)} more speeches for {name}')

            except Exception as e:
                print(f"No more speeches available or some generic error to check")
                break

        print(f'Stopped fetching list of speeches for {name}')
        logging.info(f'Stopped fetching list of speeches for {name}')

        # Fetch results from page
        speeches_available = fetch_results(driver.page_source)
        speeches_available = [(name,) + x for x in speeches_available]

        # ---- PART 2
        # Extract the content of each intervention to plenary debates

        # Find which speeches we need to scrape
        try:
            saved_df = pd.read_csv(outpath)
            already_scraped_speeches = saved_df['Url'].tolist()
            speeches_to_scrape= [
                tup for tup in speeches_available if tup[2] not in already_scraped_speeches]
            print(f"Found {len(speeches_to_scrape)} left to scrape")
            logging.info(f"Found {len(speeches_to_scrape)} left to scrape")

        except FileNotFoundError:
            saved_df = None
            speeches_to_scrape = speeches_available
            print(f"""No old file with scraped speeches at {outpath}. 
                    Skipping file reading and scraping {len(speeches_to_scrape)} speeches.""")
            logging.info(f"""Now old file with scraped speeches at {outpath}. 
                    Skipping file reading and scraping {len(speeches_to_scrape)} speeches.""")

        if len(speeches_to_scrape) > 0: 

            # Create a namedtuple with the specified field names
            mp_list = namedtuple("MpActivities", ["MP", "Date", "Language", "Title", "Url", "Content"])

            # Generate namedtuples for each element in the list
            namedtuples_list = []

            for speech in speeches_to_scrape:

                time.sleep(2)

                mp, title, url  = speech
                logging.info(f'Extracting content from  {url} for {mp}')
                content = extract_content_from_url(url, verbose = False)
                language_code = find_language_from_url(url)
                date = find_date_from_url(url)
                
                named_tuple = mp_list(MP=mp, Date=date, Language=language_code, Title=title, Url=url, Content=content)
                namedtuples_list.append(named_tuple)
            
            # Save results to a csv page
            if saved_df is not None: 
                res_df = pd.concat([saved_df, pd.DataFrame(namedtuples_list)])
            else: 
                res_df = pd.DataFrame(namedtuples_list)
            res_df.to_csv(outpath, index = False)
        
        print(f"--------------- End Processing {name}")
        logging.info(f"--------------- End Processing {name}")



def main():
    parser = argparse.ArgumentParser(description='Scrape MEPS speeches')
    parser.add_argument('input_dir', help='The location where the list of Meps to scrape is saved')
    parser.add_argument('--update', help = 'If True attempts to scrape speeches also for Meps already dealt with')
    args = parser.parse_args()

    # Configuration
    current_directory = os.path.dirname(os.path.abspath(os.getcwd()))
  
    # Load config file
    with open('../config/config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    europal_website = config['meps_speeches']['europal_website']
    href_root = config['meps_speeches']['href_root']
    output_dir = os.path.join(current_directory, config['meps_speeches']['output_dir'])
    print(output_dir)

    # Configure logging 
    logs_dir = os.path.join(current_directory, config['meps_speeches']['logs_dir'])
    logs_filename = config['meps_speeches']['logs_filename']
    print(logs_dir)

    logging.basicConfig(
        filename=os.path.join(logs_dir, logs_filename),
        level=logging.INFO, 
        format='%(asctime)s - %(levelname)s - %(message)s',
        force=True
        )

    # Load Meps list
    meps_temp = pd.read_csv(args.input_dir)

    # Check if meps were already scraped
    already_scraped_directory = os.path.join(current_directory, config['meps_speeches']['output_dir'])
    df = join_csv_files(already_scraped_directory)

    meps = meps_temp[~meps_temp['fullName'].isin(df['MP'].tolist())]
    print(args.update)

    if args.update:
        print(f"""Found {len(meps_temp)} meps to scrape""")
        scrape_speeches(meps_temp, europal_website, href_root, output_dir)
    else:
        print(f"""Found {len(meps)} meps to scrape""")
        scrape_speeches(meps, europal_website, href_root, output_dir)


if __name__ == "__main__":
    main()