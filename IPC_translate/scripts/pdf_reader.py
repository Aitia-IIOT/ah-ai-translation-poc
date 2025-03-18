import pdfplumber
import re
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

#Insert key for OpenAI
ef = OpenAIEmbeddings(api_key="XYZ")

chapters = []
elements = []

def clean_table(table):
    return [
        [cell.replace("\n", " ").strip() if isinstance(cell, str) else "" for cell in row]
        for row in table
    ]

with pdfplumber.open("./IPC-2581C.pdf") as pdf:
    pagenr = 1
    chaptername = ""
    for page in pdf.pages:        
        tables = page.extract_tables()
        for table in tables:
            for row in table:
                if (row.__contains__("0-1") or row.__contains__("0-n") or row.__contains__("1-1") or row.__contains__("1-n")):
                    #if row[0] is None:
                    for cell in row:
                        if cell is None or not isinstance(cell, str):
                            cell2 = ""
                            row[row.index(cell)] = cell2
                        else:
                            for char in cell:
                                if char == "\\":
                                    if cell[cell.index(char)+1] == "n":
                                        cell = cell.replace(char+1, "")
                                        cell = cell.replace(char, "")
                    cleaned_row = [cell.strip() for cell in row if isinstance(cell, str) and cell.strip() != ""]
                    if (table.index(row) == 3 or table.index(row) == 2 or table.index(row) == 0) and row[0][0].isupper():
                        chaptername = cleaned_row[0]
                        #print(chaptername)
                    else:
                        #print(chaptername+"."+cleaned_row[0])
                        if cleaned_row[0][0].islower() or cleaned_row[0][0] == 'O':
                            #print("ADDED: "+chaptername+"."+cleaned_row[0])
                            element_name = cleaned_row[0]
                            desc = cleaned_row[2]
                            elements.append((chaptername+"."+element_name, desc))


'''for element in elements:
    print(element)'''

cleaned_elements = []

for element in elements:
    cleaned_element = []
    for i in range(0, len(element)):
        if element[i].__contains__("\n"):
            elem = element[i].replace("\n", "").replace("�", "")
        else:
            elem = element[i]
        cleaned_element.append(elem)
    cleaned_elements.append(cleaned_element)
    
with open("variables/auto_variables.txt", "r") as f:
    data = f.read()

richer_data = []

for element in cleaned_elements:
    if data.__contains__(element[0]):
        for line in data.split("\n"):
            if line.__contains__(element[0]):
                line = line + " | " + element[1] + "\n"
                #print(line)
                richer_data.append(line)

richer_txt = ""
richer_data = sorted(richer_data)
for line in richer_data:
    richer_txt += line
with open("variables/rich_auto_variables.txt", "w", encoding="utf-8") as f:
    f.write(richer_txt)
    
db_data = []
    
with open("IPC-2581C_elements.txt", "w") as f:
    for element in cleaned_elements:
        f.write(element[0] + " | " + element[1] + "\n")
        db_data.append(element[0] + " | " + element[1] + "\n")
        
db = Chroma.from_texts(
    texts=db_data,
    embedding=ef,
    persist_directory="expanded_rag",
    collection_name="ipc2581"
)