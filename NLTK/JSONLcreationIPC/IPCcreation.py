
"""
This script is used to create a machine learning training file in jsonl format to fine-tune a model.
It uses EC xml files as inputs and transforms them into IPC-2581 xml format.
"""


import os
import json
import re

# Directory paths - change the project root according to your case
project_root = r"C:\Users\user\AITIA\ah-ai-translation-poc"
ec_directory = os.path.join(project_root, "NLTK\Models\Model_EC")  # Directory containing EC XML files
output_jsonl_file = os.path.join(project_root, "NLTK\JSONLcreationIPC\IPC_FineTuning_data.jsonl")

# Defined mappings from EC tags to IPC tags - the other EC attributes do not have a corresponding pair in the IPC schema
tag_mapping = {
    "EPPL Family": "RefDes layerRef",
    "Description": "BomItem description",
    "SPN": "BomItem internalPartNumber",
    "Component Number": "BomItem OEMDesignNumberRef",
    "Commercial Part Number": "AvlItem OEMDesingNumber",
    "Generic Part Type": "General Type",
    "Engineering Package": "Component packageRef",
    "Generic Specification": "Component refDes",
    "Moisture sensitivity level": "AvlMpn moistureSensitivity",
    "Comment": "AvlHeader comment",
    "Weight": "Component weight",
    "Manufacturer": "AvlVendor enterpriseRef",
    "Library Ref": "RefDes name",
    "Sim Model Name": "Tuning value",
    "Sim File": "Tuning value",
    "Sim Kind": "Tuning value",
    "Sim SubKind": "Tuning value",
    "Sim Netlist": "Tuning value",
    "Sim Spice Prefix": "Tuning value",
    "Sim Port Map": "Tuning value",
    "Assembly qual status": "BomHeader assembly",
    "Value": "Characteristics measuredCharacteristicsValue",
    "Tol": "Characteristics engineeringPositiveTolerance",
    "Volt": "Characteristics rangedCharacteristicsUpperValue",
    "Footprint": "Package type",
    "Application": "ChangeRec application",
    "Generic specification": "Component refDes"
}

# Grouping logic based on common XML elements
grouping = {
    "BomItem": ["Description", "SPN", "Component Number", "Assembly qual status"],
    "AvlItem": ["Commercial Part Number"],
    "Component": ["Engineering Package", "Generic Specification", "Weight"],
    "AvlMpn": ["Moisture sensitivity level"],
    "AvlHeader": ["Comment"],
    "AvlVendor": ["Manufacturer"],
    "RefDes": ["EPPL Family", "Library Ref"],
    "Tuning": ["Sim Model Name", "Sim File", "Sim Kind", "Sim SubKind", "Sim Netlist", "Sim Spice Prefix", "Sim Port Map"],
    "Characteristics": ["Value", "Tol", "Volt"],
    "Package": ["Footprint"],
    "ChangeRec": ["Application"]
}

"""
 Function to read XML content and construct JSONL entries.
 This creates one line from each complete EC file, with the corresponding IPC output. (170 lines)
"""
def create_jsonl_from_xml(ec_directory, output_jsonl_file):
    with open(output_jsonl_file, 'w', encoding='utf-8') as jsonl_out:
        for i in range(170):
            ec_filename = f"SAE_EC_DataModel.xml_{i}"
            ec_filepath = os.path.join(ec_directory, ec_filename)

            if os.path.exists(ec_filepath):
                # Process EC XML file
                with open(ec_filepath, 'r', encoding='utf-8') as ec_file:
                    ec_content = ec_file.read().strip()

                    # Dictionary to store extracted values
                    values = {key: "" for key in tag_mapping.keys()}

                    # Extract EC values using regex
                    for ec_tag in tag_mapping.keys():
                        ec_value_match = re.search(rf"<{ec_tag}>(.*?)</{ec_tag}>", ec_content, re.DOTALL)
                        if ec_value_match:
                            values[ec_tag] = ec_value_match.group(1).strip()

                    # Construct assistant message content
                    assistant_content = "<Root>\n"
                    for group, tags in grouping.items():
                        tag_values = " ".join(
                            [f'{tag_mapping[tag].split()[-1]}="{values[tag]}"' for tag in tags if values[tag]])
                        if tag_values:
                            assistant_content += f"  <{group} {tag_values} />\n"
                    assistant_content += "</Root>"

                    # Construct JSONL entry for EC XML content (user message)
                    user_message = {
                        "role": "user",
                        "content": ec_content
                    }

                    # Construct JSONL entry for assistant message
                    assistant_message = {
                        "role": "assistant",
                        "content": assistant_content.strip()
                    }

                    # Construct JSONL entry for system message
                    system_message = {
                        "role": "system",
                        "content": "You are a converter that translates the XML data of a file into XML messages of another file."
                    }

                    # Combined entry for the row, which includes the system, user and assistant message in correct order
                    row_entry = {
                        "messages": [system_message, user_message, assistant_message]
                    }

                    # Write row_entry to JSONL file
                    json.dump(row_entry, jsonl_out, ensure_ascii=False)
                    jsonl_out.write('\n')

create_jsonl_from_xml(ec_directory, output_jsonl_file)

"""
Function to teach atomic EC-IPC pairs to the model.
This creates EC-IPC connections more flexibly from the first 5 files. (63 lines)
"""
def add_individual_mapped_lines(ec_directory, output_jsonl_file):
    with open(output_jsonl_file, 'a', encoding='utf-8') as jsonl_out:
        for i in range(5):  # Limit to the first 5 files
            ec_filename = f"SAE_EC_DataModel.xml_{i}"
            ec_filepath = os.path.join(ec_directory, ec_filename)

            if os.path.exists(ec_filepath):
                # Process EC XML file
                with open(ec_filepath, 'r', encoding='utf-8') as ec_file:
                    ec_content = ec_file.read().strip()

                    # Dictionary to store extracted values
                    values = {key: "" for key in tag_mapping.keys()}

                    # Extract EC values using regex
                    for ec_tag in tag_mapping.keys():
                        ec_value_match = re.search(rf"<{ec_tag}>(.*?)</{ec_tag}>", ec_content, re.DOTALL)
                        if ec_value_match:
                            values[ec_tag] = ec_value_match.group(1).strip()

                    # Generate individual lines for each IPC pair
                    for ec_tag, ipc_tag in tag_mapping.items():
                        ipc_tag_parts = ipc_tag.split()
                        ipc_element = ipc_tag_parts[0]
                        ipc_attribute = ipc_tag_parts[1] if len(ipc_tag_parts) > 1 else ""

                        if values[ec_tag]:  # Check if there's a value to include
                            individual_assistant_content = f"<{ipc_element} {ipc_attribute}=\"{values[ec_tag]}\" />"

                            # Construct JSONL entry for assistant message
                            assistant_message = {
                                "role": "assistant",
                                "content": individual_assistant_content.strip()
                            }

                            # Construct JSONL entry for system message
                            system_message = {
                                "role": "system",
                                "content": "You are a converter that translates the XML data of a file into XML messages of another file."
                            }

                            # Construct JSONL entry for user message
                            user_message = {
                                "role": "user",
                                "content": f"<{ec_tag} value=\"{values[ec_tag]}\" />" if values[ec_tag] else ""
                            }

                            # Combined entry for the row
                            row_entry = {
                                "messages": [system_message, user_message, assistant_message]
                            }

                            # Write row_entry to JSONL file
                            json.dump(row_entry, jsonl_out, ensure_ascii=False)
                            jsonl_out.write('\n')

add_individual_mapped_lines(ec_directory, output_jsonl_file)


"""
Function to teach information through groups.
This creates new lines with the defines groups to make the model understand smaller, 
but corresponding logical components. (36 lines)
"""
def add_grouped_lines(ec_directory, output_jsonl_file):
    with open(output_jsonl_file, 'a', encoding='utf-8') as jsonl_out:
        for i in range(5):  # Limit to the first 5 files
            ec_filename = f"SAE_EC_DataModel.xml_{i}"
            ec_filepath = os.path.join(ec_directory, ec_filename)

            if os.path.exists(ec_filepath):
                # Process EC XML file
                with open(ec_filepath, 'r', encoding='utf-8') as ec_file:
                    ec_content = ec_file.read().strip()

                    # Dictionary to store extracted values
                    values = {key: "" for key in tag_mapping.keys()}

                    # Extract EC values using regex
                    for ec_tag in tag_mapping.keys():
                        ec_value_match = re.search(rf"<{ec_tag}>(.*?)</{ec_tag}>", ec_content, re.DOTALL)
                        if ec_value_match:
                            values[ec_tag] = ec_value_match.group(1).strip()

                    # Construct JSONL entries for each grouping
                    for group, tags in grouping.items():
                        # Create the EC content for this group
                        ec_tag_values = " ".join(
                            [f'<{tag}>{values[tag]}</{tag}>' for tag in tags if values[tag]]
                        )
                        ec_user_message_content = f"{ec_tag_values}"

                        # Create the IPC content for this group
                        ipc_tag_values = " ".join(
                            [f'{tag_mapping[tag].split()[-1]}="{values[tag]}"' for tag in tags if values[tag]]
                        )
                        ipc_assistant_message_content = f"<{group} {ipc_tag_values} />" if ipc_tag_values else ""

                        if ipc_assistant_message_content:
                            # Construct JSONL entry for user message (EC content)
                            user_message = {
                                "role": "user",
                                "content": ec_user_message_content
                            }

                            # Construct JSONL entry for assistant message (IPC content)
                            assistant_message = {
                                "role": "assistant",
                                "content": ipc_assistant_message_content
                            }

                            # Construct JSONL entry for system message
                            system_message = {
                                "role": "system",
                                "content": "You are a converter that translates the XML data of a file into XML messages of another file."
                            }

                            # Combined entry for the row, which includes the system, user, and assistant messages
                            row_entry = {
                                "messages": [system_message, user_message, assistant_message]
                            }

                            # Write row_entry to JSONL file
                            json.dump(row_entry, jsonl_out, ensure_ascii=False)
                            jsonl_out.write('\n')

# Execute the function
add_grouped_lines(ec_directory, output_jsonl_file)




