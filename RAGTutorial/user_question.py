#Importing neessary libraries
import customtkinter
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import OpenAIEmbeddings
import customtkinter as tk


def user_question_process(question, uq_frame, go_button, per_dir, openai_key):
    if per_dir == "":
        per_dir = "dir"
    try:
        print(per_dir)
        ############################INSERT API KEY HERE############################
        #                                                                         #
        openai_api_key = openai_key
        #                                                                         #
        ###########################################################################
    
    
    
        prompt_template = ChatPromptTemplate.from_messages([
        "system", """
            Context: You are a very useful bot, who create a short answer for a given question. You are the LLM part in a RAG model.
        
            1. Tasks:
                - You can use only data which i provided in the context. If you don't know the answer, just say that you don't know, don't try to make up an answer.
                - The context is the following: {context}
                - Do not put in page numbers, or any other information, just the important measurements and attributes, maybe the manufacturer and website, warranty, etc., but not page numbers.
                - DO NOT PUT TRIPLE BACKTICKS INTO THE ANSWER!
        
            2. Output format:
                - The output format is TXT.
            
            3. TXT format:
                - You should try to give the shortest answer possible, but it should be informative.
                - The answer should be in a single line.
            
            4. Question:
                -Here is a question: {question}

            Answer:
        """])
    
        #Loading the database from the persist directory
        vectorestore = Chroma(persist_directory=per_dir, collection_name="test_db")
        #Setting the embedding function (MUST BE THE SAME AS IN THE DATABASE)
        vectorestore._embedding_function = OpenAIEmbeddings(api_key=openai_api_key)
    
        #Creating a list of the most similar documents to the question (k (aka "top k") tells how many documents to return)
        retrieved = vectorestore.similarity_search(query=question, k=5)
    
        #Creating the LLM model
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=openai_api_key)

        #Merging the top k most similar documents into a single context
        cont_text = "".join(ret.page_content for ret in retrieved)
        print(cont_text)
        
        with open("log.txt", "w", encoding="utf-8") as f:
            for ret in retrieved:
                f.write(ret.page_content+"\n\n")
        
            
        #Inserting the context and the question into the prompt template, creating the prompt itself
        prompt = prompt_template.invoke({"context": cont_text, "question":question})
    
        #Invoking the LLM model with the prompt, and it gives back a question
        response = llm.invoke(prompt)
    
        #Parsing the response into a string
        parsrep = StrOutputParser().invoke(response)
    
        #Deleting an existing answer if there is one
        list = uq_frame.winfo_children()
        print(list)
        print(len(list))
        if len(list) > 8:
            list[-2].destroy()
            list[-1].destroy()
    
        #Creating the "Answer:" label
        cf = customtkinter.CTkFont(family="Arial", size=12).measure("Answer: ")
        ans_lab = customtkinter.CTkLabel(uq_frame, width= 175, height= 50, text_color="white", font=("Arial", 12),fg_color="transparent",bg_color="transparent", text="Answer: ")
        ans_lab.place (x=340-cf/2, y=380)
    
        #Creating the answer label to show the answer to the user
        cf = customtkinter.CTkFont(family="Arial", size=12).measure(parsrep)
        answer = customtkinter.CTkLabel(uq_frame, width= 175, height= 50, text_color="white", font=("Arial", 12),fg_color="transparent",bg_color="transparent", text=parsrep)
        answer.place (x=400-cf/2, y=420)
    
        go_button.configure(state="normal")
    
    except Exception as e:
        cf= customtkinter.CTkFont(family="Arial", size=12).measure("An error occured: ")
        error_occured = customtkinter.CTkLabel(uq_frame, width= 175, height= 50, text_color="white", font=("Arial", 12),fg_color="transparent",bg_color="transparent", text="An error occured: ")
        error_occured.place (x=340-cf/2, y=380)
        
        cf = customtkinter.CTkFont(family="Arial", size=12).measure(e)
        error = customtkinter.CTkLabel(uq_frame, width= 175, height= 50, text_color="white", font=("Arial", 12),fg_color="transparent",bg_color="transparent", text=str(e))
        error.place (x=400-cf/2, y=420)
        
        go_button.configure(state="normal")
        
        
