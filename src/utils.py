
import xml.etree.ElementTree as ET

def xml_to_dict(xml_file):
    try:
        # Parse the XML file
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Define a recursive function to convert XML elements to dictionaries
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

        # Convert the root element to a dictionary
        xml_dict = element_to_dict(root)

        return xml_dict
    except Exception as e:
        print(f"Error parsing XML: {e}")
        return None

# # Example usage:
# xml_file = 'example.xml'  # Replace with the path to your XML file
# result = xml_to_dict(xml_file)

