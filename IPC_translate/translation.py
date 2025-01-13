import pandas as pd
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import openai
import json

element_list = []

with open("IPC-2581C_elements.json", encoding="utf-8") as f:
    data = json.load(f)

name_list = [element["name"].lower() for element in data["Elements"]]

#Insert key for OpenAI

embedding_function = OpenAIEmbeddings(api_key="")

vectorestore = Chroma(persist_directory="", collection_name="")
vectorestore._embedding_function = embedding_function

#Insert Azure OpenAI parameters

openai.api_type = ""
openai.azure_endpoint = ""
openai.api_version = ""
openai.api_key = ""

#-----------------------------------------------EDDIG JO----------------------------------------------#

get_table_template = ChatPromptTemplate.from_messages([
    """
            Is the previous prompt mentions a subcomponent as an answer? If so, name it and if there is not an answer in the text then your answer needs to be "- \n". 
            
            Format example: "BOM.Component" or "Component" if there is no main component. Aka: "maincomponent.subcomponent" or "subcomponent" simply.
            
            Previous prompt answer: {paragraph}
            
            Answer:
        """])

important_template = ChatPromptTemplate.from_messages([
        """
            1. Identify Relevant Information
            
                - According to the paragraphs provided, what details are directly relevant to storing {desc}?

            2. Name a Subcomponent (and Main Component if Applicable)

                - Is there a specific subcomponent described in the paragraphs that can natively store {desc} (i.e., without hacks or repurposing)?
                - Remember that the subcomponent must genuinely support {desc} in its intended functionality (for example, you cannot just use a limited enum value to represent something else).
            
            3.Provide Proof (Mandatory)

                - In a separate paragraph, directly quote the specific text or code snippet from the given paragraphs that justifies why this subcomponent can store {desc}.
                - You must rely only on the provided paragraphs for your proof.
                
            4. XML Code Example

                - Show an XML code snippet demonstrating how this subcomponent would store {desc}.
                - Clearly highlight or emphasize the critical part of the code.
                - Write a brief explanation describing how this XML is meant to store {desc}.
                - If you identified both a main component and a subcomponent, name them using the format: maincomponent.subcomponent. Otherwise, just use subcomponent.
                
            Paragraphs: {paragraph}

            Answer:
        """])

find_subcomponent_template = ChatPromptTemplate.from_messages([
        """
            Is the previous prompt mentions a subcomponent as an answer? If so, name it and if there is not an answer in the text then your answer needs to be "- \n". 
            
            Format example: "BOM.Component" or "Component" if there is no main component. Aka: "maincomponent.subcomponent" or "subcomponent" simply.
            
            Previous prompt answer: {paragraph}
            
            Answer:
        """])

tags = pd.read_csv('TagsMeaning.csv', sep=';')
output_txt ="EC_tag;IPC_element\n"
aianswers = ""
comment = ""
untested_answers = ""

for line in tags.values:
    print(f"In which element could be stored the {line[1]}?\n")
    retrived = vectorestore.similarity_search(query=line[1], k=2)
    ret_cont="".join(ret.page_content+"\n\n\n" for ret in retrived)
    
    print("\n\n"+ret_cont+"\n\n")
    
    prompt = important_template.invoke({"desc":line[1].lower(), "paragraph":ret_cont})
    
    prompt = prompt.messages[0].content
    
    messes = [{"role": "system", "content": "You get text of two paragraphs. Answer the following questions based on the paragraphs."},
                                                                        {"role": "user", "content": prompt},]
    
    response = openai.chat.completions.create(model="gpt-4o", messages=messes)
    print(response.choices[0].message.content)
    
    aianswers += response.choices[0].message.content+"\n\n\n" 
    
    prompt = find_subcomponent_template.invoke({"desc":line[1], "paragraph":response.choices[0].message.content})
    
    prompt = prompt.messages[0].content
    
    messes = [{"role": "system", "content": "Here are the important information based on your opinion from previous prompt. You can't use other source other than this."},
              {"role": "user", "content": prompt},]
    
    response = openai.chat.completions.create(model="gpt-4o", messages=messes)
    
    ai_elements=response.choices[0].message.content.replace("Type", "").split(".")
    
    if response.choices[0].message.content.lower() in name_list:
        output_txt += line[0] + ";"+response.choices[0].message.content+"\n"
    else:
        output_txt += line[0] + "; - \n"


with open(f"output.csv", "w", encoding="utf-8") as f:
    f.write(output_txt)
    
    
with open("aianswers.txt", "w", encoding="utf-8") as f:
    f.write(aianswers)
    