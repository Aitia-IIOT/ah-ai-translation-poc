from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import shutil
import time
import customtkinter as tk
import codecs

#This function is used to update the database with new files, basically it's the same as create_db.py, but without deleting an existing database.
def update_database(files_path, go_button, vectorstore_frame, chunking_size, overlap_size, per_dir, openai_key):
    try:
        vectorstore = Chroma(collection_name="test_db", persist_directory="dir")
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
    
        for files in os.listdir(files_path):
            if files.endswith(".pdf") or files.endswith(".PDF"):
                pdfnr += 1
                loader = PyPDFLoader(files_path + "/" + files)
                pages = loader.load_and_split()
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=int(chunking_size), chunk_overlap=int(overlap_size))
                docsplits += text_splitter.split_documents(pages)
            elif files.endswith(".txt"):
                txtnr += 1
                with codecs.open(files_path + "/" + files, "r", encoding="utf-8") as f:
                    text_splitter = RecursiveCharacterTextSplitter(chunk_size=int(chunking_size), chunk_overlap=int(overlap_size))
                    txt_splitted = text_splitter.split_text(f.read())
                    textsplits.append(txt_splitted)
            elif files.endswith(".md"):
                mdnr += 1
                with open(files_path + "/" + files, "r", encoding="utf-8") as f:
                    text_splitter = RecursiveCharacterTextSplitter(chunk_size=int(chunking_size), chunk_overlap=int(overlap_size))
                    txt_splitted = text_splitter.split_text(f.read())
                    textsplits.append(txt_splitted)
    
        cf = tk.CTkFont(family="Consolas", size=12).measure("Found " + str(pdfnr) + " documents, " + str(txtnr) + " texts and " + str(mdnr) + " markdown files.")            
        founds = tk.CTkLabel(vectorstore_frame, width= 175, height= 50, text_color="white", font=("Consolas", 12),fg_color="transparent",bg_color="transparent", text="Found " + str(pdfnr) + " documents, " + str(txtnr) + " texts and " + str(mdnr) + " markdown files.")
        founds.place (x=800/2-cf/2, y=420)
                
        embedding_function = OpenAIEmbeddings(api_key=openai_key)
        combined_data = []

        if len(docsplits) > 0:
            combined_data.extend(docsplits)
            print("Documents added:", docsplits)

        if len(textsplits) > 0:
        # Convert texts to Document objects if necessary
            from langchain.schema import Document
            text_documents = [Document(page_content=text) for text in textsplits]
            combined_data.extend(text_documents)
            print("Texts added:", textsplits)

        if combined_data:
            vectorstore = Chroma.from_documents(
                documents=combined_data,
                embedding=embedding_function,
                persist_directory=per_dir,
                collection_name="test_db"
            )
        go_button.configure(fg_color="#066d29", text="Done!")
        time.sleep(2)
        go_button.configure(fg_color="#202020", text="Go")
        go_button.configure(state="normal")
        
        
    except Exception as e:
        go_button.configure(fg_color="#960e0e", text="Error!")
        time.sleep(2)
        go_button.configure(fg_color="#202020", text="Go")
        go_button.configure(state="normal")
        
        cf = tk.CTkFont(family="Consolas", size=12).measure(e)            
        founds = tk.CTkLabel(vectorstore_frame, width= 175, height= 50, text_color="white", font=("Consolas", 12),fg_color="transparent",bg_color="transparent", text=e)
        founds.place (x=800/2-cf/2, y=420)
        
    