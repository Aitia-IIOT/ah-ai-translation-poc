from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import customtkinter as tk

from langchain.schema import Document
import time

def create_datab(files_path, go_button, vectorstore_frame, chunking_size, overlap_size, per_dir, openai_key):
    try:
        docsplits = []
        textsplits = []
        pdfnr = 0
        txtnr = 0
        mdnr = 0
    
        if chunking_size == "" or chunking_size.isnumeric() == False:
            chunking_size = 200
        if overlap_size == "" or overlap_size.isnumeric() == False:
            overlap_size = 60
        if per_dir == "":
            per_dir = "dir"
    
        #For each file in the directory, check if it is a pdf, txt or md file and load it accordingly
        for files in os.listdir(files_path):
            if files.endswith(".pdf"):
                #We are creating a list of documents from PDF, so this requires a special loader
                loader = PyPDFLoader(files_path + "/" + files)
                pages = loader.load_and_split()
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=int(chunking_size), chunk_overlap=int(overlap_size))
                pdfnr += 1
                docsplits += text_splitter.split_documents(pages)
            
            #TXT and MD are simple text files, so we can just read them. Only reason they are in separate if statements is to keep track of how many of each type we have.
            elif files.endswith(".txt"):
                txtnr += 1
                with open(files_path + "/" + files, "r", encoding="utf-8") as f:
                    text_splitter = RecursiveCharacterTextSplitter(chunk_size=int(chunking_size), chunk_overlap=int(overlap_size))
                    file = [Document(page_content= str(f.read()))]
                    txt_splitted = text_splitter.split_documents(file)
                    textsplits+=txt_splitted
            elif files.endswith(".md"):
                mdnr += 1
                with open(files_path + "/" + files, "r", encoding="utf-8") as f:
                    text_splitter = RecursiveCharacterTextSplitter(chunk_size=int(chunking_size), chunk_overlap=int(overlap_size))
                    file = [Document(page_content= str(f.read()))]
                    txt_splitted = text_splitter.split_documents(file)
                    textsplits+=txt_splitted
                
        #Create a label to show how many files of each type we found
        cf = tk.CTkFont(family="Consolas", size=12).measure("Found " + str(pdfnr) + " documents, " + str(txtnr) + " texts and " + str(mdnr) + " markdown files.")            
        founds = tk.CTkLabel(vectorstore_frame, width= 175, height= 50, text_color="white", font=("Consolas", 12),fg_color="transparent",bg_color="transparent", text="Found " + str(pdfnr) + " documents, " + str(txtnr) + " texts and " + str(mdnr) + " markdown files.")
        founds.place (x=800/2-cf/2, y=420)
                
        #Setting embedding function
        embedding_function = OpenAIEmbeddings(api_key=openai_key)
        combined_data = []
    

        if len(docsplits) > 0:
            combined_data.extend(docsplits)
            print("Documents added:", docsplits)

        if len(textsplits) > 0:
        # Convert texts to Document objects if necessary
            combined_data.extend(textsplits)
            print("Texts added:", textsplits)
        

        #If there is data to add, create a vectorstore
        if combined_data:
            vectorstore = Chroma.from_documents(
                documents=combined_data,
                embedding=embedding_function,
                persist_directory=per_dir,
                collection_name="test_db"
            )
    
        #If there is already a collection in the directory, delete it and create a new one
        if vectorstore._collection.count() > len(combined_data):
            vectorstore.delete_collection()
            vectorstore = Chroma.from_documents(
                documents=combined_data,
                embedding=embedding_function,
                persist_directory=per_dir,
                collection_name="test_db"
            )
    
    
        go_button.configure(fg_color="#066d29", text="Done!")
        time.sleep(2)
        go_button.configure(fg_color="#202020", text="Go")
        #Enable the "go" button
        go_button.configure(state="normal")
    except Exception as e:
        #If an error occurs
        go_button.configure(fg_color="#960e0e", text="Error!")
        time.sleep(2)
        go_button.configure(fg_color="#202020", text="Go")
        go_button.configure(state="normal")
        cf = tk.CTkFont(family="Consolas", size=12).measure(e)            
        founds = tk.CTkLabel(vectorstore_frame, width= 175, height= 50, text_color="white", font=("Consolas", 12),fg_color="transparent",bg_color="transparent", text=e)
        founds.place (x=800/2-cf/2, y=420)
    
                
        
                
        
            
        
    