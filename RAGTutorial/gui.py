import customtkinter as tk
import os
import threading
from create_db import create_datab
from update_db import update_database
from user_question import user_question_process


global pdf_folder_path
pdf_folder_path = ""
global persist_folder_path
persist_folder_path = ""
global openai_key
openai_key = ""

#Setting basic apperance of the window
tk.set_appearance_mode("dark")

#creating the application window
root = tk.CTk()
root.title("RAG tutorial")
root.geometry("800x600")
root.resizable(False, False)

#Creating the main frame
def create_main_frame():
    for widget in root.winfo_children():
        widget.destroy()
    
    #Creating the main frame
    main_frame = tk.CTkFrame(root, bg_color="#000000", width=800, height=600)
    main_frame.pack(fill="both", expand=True)
    
    #Creating vectorstore button
    create_vectorstore_button = tk.CTkButton(main_frame, text="Create vectorstore", width=200, height=50, fg_color="#202020", hover_color="#001515", text_color="#006262", border_color="#006262", corner_radius=15, border_width=4, font=("Arial", 14), command=create_vectorstore_frame)
    create_vectorstore_button.place(x=300, y=160)
    
    
    #Update vectorstore button
    update_vectorstore_button = tk.CTkButton(main_frame, text="Update vectorstore", width=200, height=50, fg_color="#202020", hover_color="#001515", text_color="#006262", border_color="#006262", corner_radius=15, border_width=4, font=("Arial", 14), command = update_vectorstore_frame)
    update_vectorstore_button.place(x=300, y=240)
    
    
    #User question button
    user_question_button = tk.CTkButton(main_frame, text="User question", width=200, height=50, fg_color="#202020", hover_color="#001515", text_color="#006262", border_color="#006262", corner_radius=15, border_width=4, font=("Arial", 14), command=user_question_frame)
    user_question_button.place(x=300, y=320)
    
    ai_key = tk.CTkButton(main_frame, text="Set OpenAI key", width=160, height=40, fg_color="#202020", hover_color="#001515", text_color="#006262", border_color="#006262", corner_radius=15, border_width=4, font=("Arial", 14), command=set_ai_key)
    ai_key.place(x=320, y=450)
    
    #Footer label
    cf = tk.CTkFont(family="Arial", size=12).measure("© 2024 AITIA International Inc.")
    footer_label = tk.CTkLabel(main_frame, text="© 2024 AITIA International Inc.", text_color="grey", font=("Arial", 12))
    footer_label.place(x=400-cf/2, y=575)
    
def set_ai_key():
    set_key_window = tk.CTkToplevel()
    set_key_window.title("Setting OpenAI key")  
    set_key_window.geometry("500x150")
    set_key_window.resizable(False, False)
    set_key_window.attributes("-topmost", "true")
    cf = tk.CTkFont(family="Arial", size=20).measure("OpenAI key:")
    title = tk.CTkLabel(set_key_window, text="OpenAI key:", font=("Arial", 14))
    title.place(x=500/2-cf/2+10, y=20)
    
    global ai_key_entry
    ai_key_entry = tk.CTkEntry(set_key_window, width=400, height=40, fg_color="#202020", text_color="white", corner_radius=10, border_width=0, font=("Arial", 14))
    ai_key_entry.place(x=50, y=50)
    
    save_button = tk.CTkButton(set_key_window, text="Save", width=100, height=40, fg_color="#202020", hover_color="#001515", text_color="#006262", border_color="#006262", corner_radius=15, border_width=4, font=("Arial", 14), command=save_key)
    save_button.place(x=200, y=105)
    
    set_key_window.mainloop()
  
def save_key():
    global openai_key
    openai_key = ai_key_entry.get()
    print(openai_key)  
  
  
#Creating the vectorstore frame
def create_vectorstore_frame():
    #Destroying all widgets (a.k.a. cleaning the window)
    for widget in root.winfo_children():
        widget.destroy()
    
    #Creating the frame
    vectorstore_frame = tk.CTkFrame(root, bg_color="black", width=800, height=600)
    vectorstore_frame.pack(fill="both", expand=True)
    
    #Title label
    cf = tk.CTkFont(family="Arial", size=32).measure("Creating vectorstore")
    title_label = tk.CTkLabel(vectorstore_frame, text="Creating vectorstore", text_color="white", font=("Arial", 32))
    title_label.place(x=400-cf/2, y=90)
    
    #Info/help button
    info_button = tk.CTkButton(vectorstore_frame, text="i", width=25, height=25, fg_color="#202020", hover_color="#444444", text_color="#C9C9C9", border_color="#006262", corner_radius=15, border_width=0, font=("Cascadia Code", 14), command=creating_help)
    info_button.place(x=760, y=10)
    
    #Back button
    back_button = tk.CTkButton(vectorstore_frame, text="< Back", width=45, height=30, fg_color="#202020", hover_color="#444444", text_color="#D3D3D3", border_color="grey", corner_radius=15, border_width=0, font=("Arial", 14), command=create_main_frame)
    back_button.place(x=10, y=10)
    
    #Choose files button
    choosefile_button = tk.CTkButton(vectorstore_frame, text="Choose files", width=150, height=40, fg_color="#202020", hover_color="#001515", text_color="#006262", border_color="#006262", corner_radius=15, border_width=4, font=("Arial", 14), command=folder_dir_popup)
    choosefile_button.place(x=325, y=140)
    
    #Set chunking parameters
    ch_size = tk.CTkFont(family="Arial", size=14).measure("Chunk size:")
    chunking_label = tk.CTkLabel(vectorstore_frame, text="Chunk size:", text_color="white", font=("Arial", 14))
    chunking_label.place(x=395-ch_size, y=250)
    global chunking_size_tb
    chunking_size_tb = tk.CTkEntry(vectorstore_frame, width=50, height=30, fg_color="#202020", text_color="white", corner_radius=5, border_width=0, font=("Arial", 14), placeholder_text="200")
    chunking_size_tb.place(x=405, y=247)
    
    ol_size = tk.CTkFont(family="Arial", size=14).measure("Overlap size:")
    overlap_label = tk.CTkLabel(vectorstore_frame, text="Overlap size:", text_color="white", font=("Arial", 14))
    overlap_label.place(x=395-ol_size, y=300)
    global overlap_size_tb
    overlap_size_tb = tk.CTkEntry(vectorstore_frame, width=50, height=30, fg_color="#202020", text_color="white", corner_radius=5, border_width=0, font=("Arial", 14), placeholder_text="60")
    overlap_size_tb.place(x=405, y=297)
    
    
    choose_persist_dir = tk.CTkButton(vectorstore_frame, text="Choose persist folder", width=200, height=40, fg_color="#202020", hover_color="#001515", text_color="#006262", border_color="#006262", corner_radius=15, border_width=4, font=("Arial", 14), command=perfolder_dir_popup)
    choose_persist_dir.place(x=300, y=190)
    
    #Go button
    global go_button
    go_button = tk.CTkButton(vectorstore_frame, text="Go", width=100, height=50, fg_color="#202020", hover_color="#001515", text_color="#006262", border_color="#006262", corner_radius=15, border_width=4, font=("Arial", 14), command=create_db)
    go_button.place(x=350, y=370)
    
    #Footer label
    cf = tk.CTkFont(family="Arial", size=12).measure("© 2024 AITIA International Inc.")
    footer_label = tk.CTkLabel(vectorstore_frame, text="© 2024 AITIA International Inc.", text_color="grey", font=("Arial", 12))
    footer_label.place(x=400-cf/2, y=575)
    

#Creating the update vectorstore frame
def update_vectorstore_frame():
    for widget in root.winfo_children():
        widget.destroy()
    
    #Creating the frame
    vectorstore_frame = tk.CTkFrame(root, bg_color="black", width=800, height=600)
    vectorstore_frame.pack(fill="both", expand=True)
    
    #Title label
    cf = tk.CTkFont(family="Arial", size=32).measure("Updating vectorstore")
    title_label = tk.CTkLabel(vectorstore_frame, text="Updating vectorstore", text_color="white", font=("Arial", 32))
    title_label.place(x=400-cf/2, y=90)
    
    #Info/help button
    info_button = tk.CTkButton(vectorstore_frame, text="i", width=25, height=25, fg_color="#202020", hover_color="#444444", text_color="#C9C9C9", border_color="#006262", corner_radius=15, border_width=0, font=("Cascadia Code", 14), command=updating_help)
    info_button.place(x=760, y=10)
    
    #Back button
    back_button = tk.CTkButton(vectorstore_frame, text="< Back", width=45, height=30, fg_color="#202020", hover_color="grey", text_color="#D3D3D3", border_color="grey", corner_radius=15, border_width=0, font=("Arial", 14), command=create_main_frame)
    back_button.place(x=10, y=10)
    
    #Choose files button
    choosefile_button = tk.CTkButton(vectorstore_frame, text="Choose files", width=150, height=40, fg_color="#202020", hover_color="#001515", text_color="#006262", border_color="#006262", corner_radius=15, border_width=4, font=("Arial", 14), command=folder_dir_popup)
    choosefile_button.place(x=325, y=140)
    
    
    ch_size = tk.CTkFont(family="Arial", size=14).measure("Chunk size:")
    chunking_label = tk.CTkLabel(vectorstore_frame, text="Chunk size:", text_color="white", font=("Arial", 14))
    chunking_label.place(x=395-ch_size, y=250)
    global chunking_size_tb
    chunking_size_tb = tk.CTkEntry(vectorstore_frame, width=50, height=30, fg_color="#202020", text_color="white", corner_radius=5, border_width=0, font=("Arial", 14), placeholder_text="200")
    chunking_size_tb.place(x=405, y=247)
    
    ol_size = tk.CTkFont(family="Arial", size=14).measure("Overlap size:")
    overlap_label = tk.CTkLabel(vectorstore_frame, text="Overlap size:", text_color="white", font=("Arial", 14))
    overlap_label.place(x=395-ol_size, y=300)
    global overlap_size_tb
    overlap_size_tb = tk.CTkEntry(vectorstore_frame, width=50, height=30, fg_color="#202020", text_color="white", corner_radius=5, border_width=0, font=("Arial", 14), placeholder_text="60")
    overlap_size_tb.place(x=405, y=297)
    
    choose_persist_dir = tk.CTkButton(vectorstore_frame, text="Choose persist folder", width=200, height=40, fg_color="#202020", hover_color="#001515", text_color="#006262", border_color="#006262", corner_radius=15, border_width=4, font=("Arial", 14), command=perfolder_dir_popup)
    choose_persist_dir.place(x=300, y=190)
    
    #Go button
    global go_button
    go_button = tk.CTkButton(vectorstore_frame, text="Go", width=100, height=50, fg_color="#202020", hover_color="#001515", text_color="#006262", border_color="#006262", corner_radius=15, border_width=4, font=("Arial", 14), command=update_db)
    go_button.place(x=350, y=360)
    
    #Footer label
    cf = tk.CTkFont(family="Arial", size=12).measure("© 2024 AITIA International Inc.")
    footer_label = tk.CTkLabel(vectorstore_frame, text="© 2024 AITIA International Inc.", text_color="grey", font=("Arial", 12))
    footer_label.place(x=400-cf/2, y=575)
    

#Popup for choosing the folder
def folder_dir_popup(): 
    path = '{}'.format(tk.filedialog.askdirectory(title="Select PDF folder", initialdir="/", mustexist=True))
    global pdf_folder_path
    pdf_folder_path = path
    print(pdf_folder_path)
    
def perfolder_dir_popup(): 
    path = '{}'.format(tk.filedialog.askdirectory(title="Select persist folder", initialdir="/", mustexist=True))
    global persist_folder_path
    persist_folder_path = path
    

#Creating the database
def create_db():
    if pdf_folder_path == "":
        return
    t1 = threading.Thread(target=create_datab, args=(pdf_folder_path, go_button, root, chunking_size_tb.get(), overlap_size_tb.get(), persist_folder_path, openai_key))
    t1.start()
    go_button.configure(state="disabled")


#Updating the database
def update_db():
    if pdf_folder_path == "":
        return
    t1 = threading.Thread(target=update_database, args=(pdf_folder_path, go_button, root, chunking_size_tb.get(), overlap_size_tb.get(), persist_folder_path, openai_key))
    t1.start()
    go_button.configure(state="disabled")


#Creating the user question frame
def user_question_frame():
    for widget in root.winfo_children():
        widget.destroy()
    
    #Creating the frame
    global uq_frame
    uq_frame = tk.CTkFrame(root, bg_color="black", width=800, height=600)
    uq_frame.pack(fill="both", expand=True)
    
    #Creating the user question entry
    global user_question
    user_question = tk.CTkEntry(uq_frame, width=400, height=40, fg_color="#202020", text_color="white", corner_radius=10, border_width=0, font=("Arial", 14))
    user_question.place(x=200, y=180)
    
    #Cf is the width of the text, so we can center it
    cf = tk.CTkFont(family="Arial", size=14).measure("Enter your question here:")
    
    #Question label
    question_label = tk.CTkLabel(uq_frame, text="Enter your question here:", text_color="white", font=("Arial", 14))
    question_label.place(x=400-cf/2, y=150)
    
    #Title label
    cf = tk.CTkFont(family="Arial", size=32).measure("User question")
    title_label = tk.CTkLabel(uq_frame, text="User question", text_color="#006262", font=("Arial", 32))
    title_label.place(x=400-cf/2, y=70)
    
    #Info/help button
    info_button = tk.CTkButton(uq_frame, text="i", width=25, height=25, fg_color="#202020", hover_color="#444444", text_color="#C9C9C9", border_color="#006262", corner_radius=15, border_width=0, font=("Cascadia Code", 14), command=user_answer_help)
    info_button.place(x=760, y=10)
    
    #Back button
    back_button = tk.CTkButton(uq_frame, text="< Back", width=45, height=30, fg_color="#202020", hover_color="grey", text_color="#D3D3D3", border_color="grey", corner_radius=15, border_width=0, font=("Arial", 14), command=create_main_frame)
    back_button.place(x=10, y=10)
    
    choose_persist_dir = tk.CTkButton(uq_frame, text="Choose persist folder", width=200, height=40, fg_color="#202020", hover_color="#001515", text_color="#006262", border_color="#006262", corner_radius=15, border_width=4, font=("Arial", 14), command=perfolder_dir_popup)
    choose_persist_dir.place(x=300, y=240)
    
    #Go button
    global go_button
    go_button = tk.CTkButton(uq_frame, text="Go", width=100, height=50, fg_color="#202020", hover_color="#001515", text_color="#006262", border_color="#006262", corner_radius=15, border_width=4, font=("Arial", 14), command=usr_qst)
    go_button.place(x=350, y=300)
    
    #Footer label
    cf = tk.CTkFont(family="Arial", size=12).measure("© 2024 AITIA International Inc.")
    footer_label = tk.CTkLabel(uq_frame, text="© 2024 AITIA International Inc.", text_color="grey", font=("Arial", 12))
    footer_label.place(x=400-cf/2, y=575)
    

#Processing the user question
def usr_qst():
    if user_question.get() == "":
        return
    go_button.configure(state="disabled")
    t1 = threading.Thread(target=user_question_process, args=(user_question.get(),uq_frame, go_button, persist_folder_path, openai_key))
    t1.start()
    
  
  
#Creating the help windows for database creation
def creating_help():
    creating_help = tk.CTkToplevel()
    creating_help.title("Creating vectorstore help")
    creating_help.geometry("480x275")
    creating_help.resizable(False, False)
    creating_help.attributes("-topmost", "true")
    cf = tk.CTkFont(family="Arial", size=20).measure("How we create a vectorstore?")
    title = tk.CTkLabel(creating_help, text="How we create a vectorstore?", font=("Arial", 20))
    title.place(x=480/2-cf/2, y=20)
    first_step = tk.CTkLabel(creating_help, text="1. Choose the folder where the files are located.", font=("Arial", 11))
    first_step.place(x=10, y=70)
    
    second_step = tk.CTkLabel(creating_help, text="2. Click on the 'Go' button.", font=("Arial", 11))
    second_step.place(x=10, y=100)
    
    third_step = tk.CTkLabel(creating_help, text="3. The program starts reading out the text out of the selected files.", font=("Arial", 11)) 
    third_step.place(x=10, y=130)
    
    fourth_step = tk.CTkLabel(creating_help, text="4. Creating smaller chunks from the text with the given length and outlap size.", font=("Arial", 11))
    fourth_step.place(x=10, y=160)
    
    fifth_step = tk.CTkLabel(creating_help, text="5. Embedding the chunks into a x-dimension vector.", font=("Arial", 11))
    fifth_step.place(x=10, y=190)
    
    sixth_step = tk.CTkLabel(creating_help, text="6. Storing the vectors in a SQLite3 database.", font=("Arial", 11))
    sixth_step.place(x=10, y=220)
    
    creating_help.mainloop()
    
#Creating the help windows for database updating
def updating_help():
    updating_help = tk.CTkToplevel()
    updating_help.title("Creating vectorstore help")
    updating_help.geometry("500x330")
    updating_help.resizable(False, False)
    updating_help.attributes("-topmost", "true")
    cf = tk.CTkFont(family="Arial", size=20).measure("How we update a vectorstore?")
    title = tk.CTkLabel(updating_help, text="How we update a vectorstore?", font=("Arial", 20))
    title.place(x=480/2-cf/2, y=20)
    first_step = tk.CTkLabel(updating_help, text="1. Load the database by creating a ChromaDB with the persist folder.", font=("Arial", 11))
    first_step.place(x=10, y=70)
    
    second_step = tk.CTkLabel(updating_help, text="2. Set the exact same embedding function.", font=("Arial", 11))
    second_step.place(x=10, y=100)
    
    third_step = tk.CTkLabel(updating_help, text="3. Choose the folder where the files are located.", font=("Arial", 11))
    third_step.place(x=10, y=130)
    
    fourth_step = tk.CTkLabel(updating_help, text="4. Click on the 'Go' button.", font=("Arial", 11))
    fourth_step.place(x=10, y=160)
    
    fifth_step = tk.CTkLabel(updating_help, text="5. The program starts reading out the text out of the selected files.", font=("Arial", 11)) 
    fifth_step.place(x=10, y=190)
    
    sixth_step = tk.CTkLabel(updating_help, text="6. Creating smaller chunks from the text with the given length and outlap size.", font=("Arial", 11))
    sixth_step.place(x=10, y=220)
    
    seventh_step = tk.CTkLabel(updating_help, text="7. Embedding the chunks into a x-dimension vector.", font=("Arial", 11))
    seventh_step.place(x=10, y=250)
    
    eight_step = tk.CTkLabel(updating_help, text="8. Appending the list of vectors in the loaded database.", font=("Arial", 11))
    eight_step.place(x=10, y=280)
    
    updating_help.mainloop()


#Creating the help windows for user question
def user_answer_help():
    user_ans_help = tk.CTkToplevel()
    user_ans_help.title("Creating vectorstore help")
    user_ans_help.geometry("500x370")
    user_ans_help.resizable(False, False)
    user_ans_help.attributes("-topmost", "true")
    cf = tk.CTkFont(family="Arial", size=20).measure("How do we answer a user's question?")
    title = tk.CTkLabel(user_ans_help, text="How do we answer a user's question?", font=("Arial", 20))
    title.place(x=480/2-cf/2, y=20)
    first_step = tk.CTkLabel(user_ans_help, text="1. Load the database by creating a ChromaDB with the persist folder.", font=("Arial", 11))
    first_step.place(x=10, y=70)
    
    second_step = tk.CTkLabel(user_ans_help, text="2. Set the exact same embedding function.", font=("Arial", 11))
    second_step.place(x=10, y=100)
    
    third_step = tk.CTkLabel(user_ans_help, text="3. Create a prompt, which tells the LLM what to do exactly.", font=("Arial", 11))
    third_step.place(x=10, y=130)
    
    fourth_step = tk.CTkLabel(user_ans_help, text="4. Write a question in the textbox.", font=("Arial", 11))
    fourth_step.place(x=10, y=160)
    
    fifth_step = tk.CTkLabel(user_ans_help, text="5. Click on the 'Go' button.", font=("Arial", 11))
    fifth_step.place(x=10, y=190)
    
    sixth_step = tk.CTkLabel(user_ans_help, text="6. The program reads out the given question.", font=("Arial", 11)) 
    sixth_step.place(x=10, y=220)
    
    seventh_step = tk.CTkLabel(user_ans_help, text="7. The Chroma database gives back the top k chunks by the similarity of vectors.", font=("Arial", 11))
    seventh_step.place(x=10, y=250)
    
    eight_step = tk.CTkLabel(user_ans_help, text="8. Insert the top k chunk and the question into the created prompt.", font=("Arial", 11))
    eight_step.place(x=10, y=280)
    
    ninth_step = tk.CTkLabel(user_ans_help, text="9. Run the prompt into the given LLM.", font=("Arial", 11))
    ninth_step.place(x=10, y=310)
    
    tenth_step = tk.CTkLabel(user_ans_help, text="10. Parse the response and show it to the user.", font=("Arial", 11))
    tenth_step.place(x=10, y=340)
    
    user_ans_help.mainloop()

#Starting the application
create_main_frame()

#Running the main loop
root.mainloop()