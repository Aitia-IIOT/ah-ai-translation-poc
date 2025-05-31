#-----------------Importing libraries-----------------#
import pandas as pd
import numpy as np
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
import openai
#-----------------------------------------------------#

#--------------------AI imports-----------------------#
#Insert OpenAI key for embedding function
embedding_func = OpenAIEmbeddings(api_key="xyz")

#Insert Azure OpenAI parameters
openai.api_type = "xyz"
openai.azure_endpoint = "xyz"
openai.api_version = "xyz"
openai.api_key = "xyz"
#-----------------------------------------------------#

#--------------------Templates------------------------#
choosing_template = ChatPromptTemplate.from_messages([
        """
            There is multiple source tag translated to the same output element. Unfortunately, the output element most be unique.
            So you need to choose the most relevant tag for the output element and we will search another tag for the others.
            You need to give me back the tag which is the most relevant for the output element. Just the source tag, nothing else, not even a dot.
        
            Output tag(third column is the description, columns seperated with '|' ):
            {output}
            
            And here are the source tags, in the first column you see the tag name, then the description:
            {input}
            
            Answer:
        """])

comparing_template = ChatPromptTemplate.from_messages([
        """
            We want to translate between 2 standards. 
            
            There is the description of the sourcee standard: {desc}
            
            And here is the two most relevant paragraphs from the output standard: {paragraph}
            
            Based on the information above, answer these:
            
            1. Any of them is capable to store natevily the source standard (First column is the element name)? If so, name the element.
            1.2. If both of them are capable to store the source standard, then choose one, and only write about it.
            
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

#---------------------Function------------------------#
def check_dupe(file):
    
    #-----------------Data import--------------------#
    tags = pd.read_csv(file, sep=';')       #All
    tag_description = pd.read_csv('TagsMeaning.csv', sep=';')

    with open("variables/variables.txt", encoding="utf-8") as f:
        data = f.read().split("\n")

    data2 = data    #We are going to remove the used tags from this list and the other needs to be untouched.
    
    seen = set()
    dupes = []
    #-----------------------------------------------#
    
    #----------------Gathering dupes----------------#
    chosen_tags = []
    for x in tags['IPC_element'].values:
        for line in data:
            if line.__contains__(x):
                chosen_tags.append(line)
                break
    

    for x in tags['IPC_element'].values:
        if x not in seen:
            seen.add(x)
        else:
            if x not in dupes:
                if x != "-":
                    dupes.append(x)
    #----------------------------------------------#
    
    #--Gathering the EC tags for the same output--#            
    for element in dupes:
        dupe_ec_desc = ""
        dupe_ec_tag = tags[tags['IPC_element'] == element]['EC_tag'].values
        wanted_line = ""     #Also the description of the dupe IPC element, so we can descide who can keep it by being the most relevant tag.
        for line in data:   
            if line.__contains__(element):
                wanted_line = line
                break
        for y in tag_description.values:
            if y[0] in dupe_ec_tag:
                dupe_ec_desc += y[0]+' ; '+y[1] + '\n'
    #--------------------------------------------#
    
        #-----------Who can keep it--------------#
        prompt = choosing_template.invoke({"output": wanted_line, "input": dupe_ec_desc})
        prompt = prompt.messages[0].content
        
        message = [{"role": "user", "content": prompt}]
        
        response = openai.chat.completions.create(model="gpt-4o", messages=message)
        idx = np.where(dupe_ec_tag == response.choices[0].message.content)[0][0]
        dupe_ec_tag = np.delete(dupe_ec_tag, idx)
        
        for x in chosen_tags:               #|
            if data2.__contains__(x):       #|Removing the used IPC elements from the list
                data2.pop(data.index(x))    #|
        
        db = Chroma.from_texts(
            texts=data2,
            embedding=embedding_func
        )
        
        dupe_ec_desc = dupe_ec_desc.split("\n")
        dupe_ec_desc.pop()  #Removing the last empty line (there is a \n at the end of the element, creating an empty value in the list)
        dupe_ec_desc.pop(idx) #Removing the chosen tag (who keeps the IPC tag) from the list
        #---------------------------------------#
        
        #---------Looking for new tags----------#
        for y in dupe_ec_desc:      #Iterating through the EC tags which are not chosen
            new_res = db.similarity_search(query=y.split(';')[1], k=2)
            new_res = "".join(ret.page_content+"\n\n\n" for ret in new_res)
            
            prompt = comparing_template.invoke({"desc":y.split(';')[1], "paragraph":new_res})
            prompt = prompt.messages[0].content
            
            message = [{"role": "user", "content": prompt}]
            response = openai.chat.completions.create(model="gpt-4o", messages=message)
            
            prompt = extracting_template.invoke({"paragraph":response.choices[0].message.content})
            prompt = prompt.messages[0].content
            
            message = [{"role": "user", "content": prompt}]
            response = openai.chat.completions.create(model="gpt-4o", messages=message)
            
            print(y.split(';')[0][:-1]+" ; "+response.choices[0].message.content)
            
            tags.loc[tags['EC_tag'] == y.split(';')[0][:-1], 'IPC_element'] = response.choices[0].message.content
        #--------------------------------------#    

    tags.to_csv(file, sep=';', index=False)
#-----------------------------------------------------#
    
    
if __name__ == "__main__":      #|
    check_dupe('mapping.csv')   #|For testing