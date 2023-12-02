

import argparse
import pandas as pd
import requests
import xml.etree.ElementTree as ET


def fetch_xml_data(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return None


def xml_to_dict(xml_data):
    try:
        root = ET.fromstring(xml_data.encode('utf-8'))
        
        def element_to_dict(element):
            if len(element) == 0:
                return element.text
            result = {}
            for child in element:
                child_dict = element_to_dict(child)
                if child.tag in result:
                    if isinstance(result[child.tag], list):
                        result[child.tag].append(child_dict)
                    else:
                        result[child.tag] = [result[child.tag], child_dict]
                else:
                    result[child.tag] = child_dict
            return result
        
        xml_dict = element_to_dict(root)
        return xml_dict
    except ET.ElementTree.ParseError as e:
        print(f"Error parsing XML: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description='Fetch XML data from a given URL and save to a file.')
    parser.add_argument('url', help='The URL to fetch XML data from.')
    parser.add_argument('--output', help='The location to save the output file.')

    try:
        args = parser.parse_args()
        input_url = args.url
        output_file = args.output

        # Check if the input is likely a URL by looking for common URL patterns
        if '://' in input_url:
            xml_data = fetch_xml_data(input_url)

            if xml_data is not None:

                parsed_data = xml_to_dict(xml_data)

                if parsed_data is not None:
                    df = pd.DataFrame.from_dict(parsed_data['mep'])

                    if output_file:
                        df.to_csv(output_file, index = False)
                        print(f"Data fetched and saved successfully to the specificed location")
                    else:
                        print(f"Data fetched successfully:\n{xml_data}")
                else:
                    print("Function returned an empty set, please check your url")
        else:
            print("Warning: The provided argument doesn't seem to be a valid URL.")
    except argparse.ArgumentError:
        print("Error: Please provide the correct number of arguments. Use 'python script.py --help' for usage information.")

if __name__ == "__main__":
    main()

