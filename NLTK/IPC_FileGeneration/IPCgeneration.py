"""
This file was used to generate IPC-2581 formatted xml data from the EC files.
It uses the custom fine-tuned language model, to convert the data into the expected format.
"""

import os
from openai import OpenAI

# Set up OpenAI API key
api_key = 'Enter your OpenAI api-key here, or through an environment variable as api_key'
client = OpenAI(api_key=api_key)

# Define relative paths based on the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ec_directory = os.path.join(project_root, 'NLTK', 'Models', 'Model_EC')
ipc_directory = os.path.join(project_root, 'NLTK', 'Models', 'Model_IPC2581')
os.makedirs(ipc_directory, exist_ok=True)

# Function to process each EC file and generate IPC files
def process_ec_files(ec_directory, ipc_directory):
    ec_files = [f for f in os.listdir(ec_directory) if f.startswith('SAE_EC_DataModel.xml_')]

    for ec_file in ec_files:
        ec_filepath = os.path.join(ec_directory, ec_file)
        with open(ec_filepath, 'r', encoding='utf-8') as file:
            ec_content = file.read().strip()

        # Construct messages for the API
        messages = [
            {"role": "system",
             "content": "You are a converter that translates the XML data of a file into XML messages of another file."},
            {"role": "user", "content": ec_content}
        ]

        # Call the OpenAI API to get the conversion
        response = client.chat.completions.create(
            model="ft:gpt-3.5-turbo-0125:aitia-international-zrt:ectoipctranslator:9oqCfvW7",
            messages=messages,
            temperature=0
        )

        # Extract the assistant's message (the converted IPC content)
        ipc_content = response.choices[0].message.content

        # Define the output IPC file path
        # Ensure the IPC filename matches the EC filename but with "IPC_" prefix
        ipc_filename = f"IPC_{ec_file}"
        ipc_filepath = os.path.join(ipc_directory, ipc_filename)

        # Save the IPC content to the file
        with open(ipc_filepath, 'w', encoding='utf-8') as ipc_file:
            ipc_file.write(ipc_content)

        print(f"Processed {ec_file} and saved as {ipc_filename}")

# Execute the function
process_ec_files(ec_directory, ipc_directory)

