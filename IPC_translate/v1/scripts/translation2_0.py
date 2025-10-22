#----------------Importing libraries-----------------#
import pandas as pd
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
import openai
import json
from duplicate_output_detection import check_dupe
#-----------------------------------------------------#

#--------------------AI imports-----------------------#
#Insert OpenAI key for embedding function
embedding_function = OpenAIEmbeddings(api_key="xyz")

#Import Chroma database
vectorestore = Chroma(persist_directory="combined_rag", collection_name="ipc2581")
vectorestore._embedding_function = embedding_function

#Insert Azure OpenAI parameters
openai.api_type = "xyz"
openai.azure_endpoint = "xyz"
openai.api_version = "xyz"
openai.api_key = "xyz"
#-----------------------------------------------------#

#--------------------Templates------------------------#
comparing_template = ChatPromptTemplate.from_messages([
        """
            We want to translate between 2 standards. 
            
            There is the description of the source standard: {desc}
            
            And here is the two most relevant paragraphs from the output standard: {paragraph}
            
            Based on the information above, answer these:
            
            1. Any of them is capable to store natevily the source standard (First column is the element name, second is the type)? If so, name the element.
            
            2. Why do you think that?
        
            Answer:
        """])

extracting_template = ChatPromptTemplate.from_messages([
        """
            If the input text says that a subcomponent is capable to store the source standard, then name the component. If there is no component which able to store data, then your answer needs to be "- \n".
            Input: {paragraph}
            
            Do not put ' or any other special characters in the answer, because the output will be used in futher methods.
        
            Answer:
        """])
#-----------------------------------------------------#

#--------------------Data import-----------------------#
tags = pd.read_csv('TagsMeaning.csv', sep=';')
output_txt ="EC_tag;IPC_element\n"
#-----------------------------------------------------#

#--------------------Main loop-------------------------#
for line in tags.values:   #Iteraiting through EC tags in TagsMeaning.csv
    retrived = vectorestore.similarity_search(query=line[1], k=2)     #|
    ret_cont="".join(ret.page_content+"\n\n\n" for ret in retrived)   #| Searching for the most relevant elements by the description of EC tag
    
    prompt = comparing_template.invoke({"desc":line[1].lower(), "paragraph":ret_cont})  #Inserting the description of EC tag and the most relevant elements into the prompt template converting it to a prompt
    
    prompt = prompt.messages[0].content  #Extracting the prompt's content (Azure OpenAI API needs only the content, vs ChatGPT where the whole object is needed)
    
    prompt_list = [{"role": "system", "content": "You get text of two paragraphs. Answer the following questions based on the paragraphs."}, #Creating the message list for the Azure OpenAI API
                                                                        {"role": "user", "content": prompt},]
    
    response = openai.chat.completions.create(model="gpt-4o", messages=prompt_list)  
    
    prompt = extracting_template.invoke({"paragraph":response.choices[0].message.content}) #response.choices[0].message.content is the actual answer from the API call
    
    prompt = prompt.messages[0].content
    
    prompt_list = [{"role": "system", "content": "Here are the important information based on your opinion from previous prompt. You can't use other source other than this."},
              {"role": "user", "content": prompt},]
    
    response = openai.chat.completions.create(model="gpt-4o", messages=prompt_list)
    
    output_txt += line[0] + ";"+response.choices[0].message.content+"\n"


with open(f"onlab/10.csv", "w", encoding="utf-8") as f:    #|
    f.write(output_txt)                                   #| Seems useless, but it's easier to work with numpy array from this point 
    
is_there_a_dupe = True   #We need to check if there are any duplicates in the output file

tags = pd.read_csv('onlab/10.csv', sep=';')     #Creating the numpy array
dupes = []
seen = set()

for x in tags['IPC_element'].values:    #Iterating through the IPC elements in the output file
    if x not in seen:                       #If the element is not been seen yet, add it to the set
        seen.add(x)
    else:                                   #If the element is already in the set, add it to the dupes list
        if x not in dupes:
            if x != "-":                        #Except empty elements
                dupes.append(x)

if len(dupes) == 0:                 #|
    is_there_a_dupe = False         #|If there are no duplicates, we can skip the loop
    
while is_there_a_dupe:
    check_dupe('mapping.csv')    #Swapping the duplicates
    tags = pd.read_csv('mapping.csv', sep=';')
    dupes.clear()
    seen.clear()
    
    for x in tags['IPC_element'].values:
        if x not in seen:
            seen.add(x)
        else:
            if x not in dupes:
                if x != "-":
                    dupes.append(x)
    
    if len(dupes) == 0:
        is_there_a_dupe = False
        
#-----------------------------------------------------#