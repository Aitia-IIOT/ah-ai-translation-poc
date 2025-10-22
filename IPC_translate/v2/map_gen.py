from auto_tree import auto_tree
from auto_var2 import auto_var2
from pdf_reader import pdf_reader
from translation import translation
import os

if __name__ == "__main__":
    try:
        if not os.path.exists("mapping_table/EC_IPC.csv"):
            auto_tree()
            print("-----")
            auto_var2()
            print("-----")
            pdf_reader()
            print("-----")
            translation()
        else:
            print("Mapping table already exists.")
    except Exception as e:
        print ("Error: "+str(e)) 