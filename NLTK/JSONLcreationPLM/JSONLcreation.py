"""
This script can be used to extend the content of the PLM files with new XML tags.
The way to do it, is creating a training file in jsonl format, then fine-tuning a model with the training file.
After that we can instruct our model (for example in jupyter notebook or visual studio code) to create our modified files.
"""


import datetime
import os
import json
import re

# Directory paths - the project_root variable likely needs setting from another computer, the others are relative
project_root = r"C:\Users\user\AITIA\ah-ai-translation-poc"

ec_directory = os.path.join(project_root, "NLTK\Models\Model_EC")  # Directory containing EC XML files
plm_directory = os.path.join(project_root, "NLTK\Models\Model_PLM")  # Directory containing PLM XML files
output_jsonl_file = os.path.join(project_root, "NLTK\JSONLcreationPLM\FineTuning_data.jsonl")

#output_directory = os.path.dirname(output_jsonl_file)
#os.makedirs(output_directory, exist_ok=True)
# Function to read XML content and construct JSONL entries
def create_jsonl_from_xml(ec_directory, plm_directory, output_jsonl_file):
    with open(output_jsonl_file, 'w', encoding='utf-8') as jsonl_out:
        for i in range(170):
            ec_filename = f"SAE_EC_DataModel.xml_{i}"
            ec_filepath = os.path.join(ec_directory, ec_filename)
            plm_filename = f"SAE_PLM_DataModel.xml_{i}"
            plm_filepath = os.path.join(plm_directory, plm_filename)

            if os.path.exists(ec_filepath) and os.path.exists(plm_filepath):
                # Process EC XML file
                with open(ec_filepath, 'r', encoding='utf-8') as ec_file:
                    ec_content = ec_file.read().strip()

                    """
                    Extracting values from EC XML using regex.
                    Each new xml tag needs a match and a value variable as shown below.
                    If the value is null, then just return an empty string.
                    """
                    application_match = re.search(r"<Application>(.*?)</Application>", ec_content, re.DOTALL)
                    if application_match:
                        application_value = application_match.group(1).strip()
                    else:
                        application_value = ""

                    generic_specification_match = re.search(r"<Generic specification>(.*?)</Generic specification>", ec_content, re.DOTALL)
                    if generic_specification_match:
                        generic_specification_value = generic_specification_match.group(1).strip()
                    else:
                        generic_specification_value = ""

                    detail_specification_match = re.search(r"<Detail specification>(.*?)</Detail specification>",
                                                            ec_content, re.DOTALL)
                    if detail_specification_match:
                        detail_specification_value = detail_specification_match.group(1).strip()
                    else:
                        detail_specification_value = ""

                    ebom_match = re.search(r"<PPL EBOM>(.*?)</PPL EBOM>",
                                                           ec_content, re.DOTALL)
                    if ebom_match:
                        ebom_value = ebom_match.group(1).strip()
                    else:
                        ebom_value = ""

                    mbom_match = re.search(r"<PPL MBOM>(.*?)</PPL MBOM>",
                                           ec_content, re.DOTALL)
                    if mbom_match:
                        mbom_value = mbom_match.group(1).strip()
                    else:
                        mbom_value = ""

                    reffiles_match = re.search(r"<Link files>(.*?)</Link files>",
                                           ec_content, re.DOTALL)
                    if reffiles_match:
                        reffiles_value = reffiles_match.group(1).strip()
                    else:
                        reffiles_value = ""


                    # Construct JSONL entry for EC XML content (user message)
                    user_message = {
                        "role": "user",
                        "content": ec_content
                    }

                # Process PLM XML file
                with open(plm_filepath, 'r', encoding='utf-8') as plm_file:
                    plm_content = plm_file.read().strip()
                    # A variable to add value to the <Modification Date> tag
                    current_date = datetime.datetime.now().strftime("%d-%m-%Y")

                    # Regex replacement to update <Modification Date>
                    plm_content_updated = re.sub(r"<Modification Date>(.*?)</Modification Date>",
                                                 f"<Modification Date>{current_date}</Modification Date>",
                                                 plm_content)
                    """
                    This is how we can add the new tags to the content of the PLM files in the training file.
                    Each new tag will be added in order before the closing </row> regular expression.
                    """
                    plm_content_with_new_tags = re.sub(r"(</row>)", f"<App>{application_value}</App>\n   "
                                                                    f"<GenericSpecification>{generic_specification_value}</GenericSpecification>\n   "
                                                                    f"<DetailSpecification>{detail_specification_value}</DetailSpecification>\n   "
                                                                    f"<EBOMstatus>{ebom_value}</EBOMstatus>\n   "
                                                                    f"<MBOMstatus>{mbom_value}</MBOMstatus>\n   "
                                                                    f"<ReferenceFiles>{re.escape(reffiles_value)}</ReferenceFiles>\n   "
                                                                    #Here you can add more tags with values as shown above.
                                                                    f"\\1", plm_content_updated,
                                                  flags=re.DOTALL)

                    # Construct JSONL entry for assistant message
                    assistant_message = {
                        "role": "assistant",
                        "content": plm_content_with_new_tags
                    }

                # Construct JSONL entry for system message
                system_message = {
                    "role": "system",
                    "content": "You are a converter, that translates the XML data of a file into XML messages of another one."
                }

                # Combined entry for the row, which includes the system, user and assistant message in correct order
                row_entry = {
                    "messages": [system_message, user_message, assistant_message]
                }

                # Write row_entry to JSONL file
                json.dump(row_entry, jsonl_out, ensure_ascii=False)
                jsonl_out.write('\n')

# Execute the function
create_jsonl_from_xml(ec_directory, plm_directory, output_jsonl_file)