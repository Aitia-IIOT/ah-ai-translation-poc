#----------Importing libraries--------------#
import pandas as pd
from find_element_in_tree import find_element
#------------------------------------------#

#-----Creating variables and read data-----#
xml_content = ""
output_xml = ""
formed_xml = ""
with open("SAE_EC_DataModel.xml", "r") as f:
    xml_content = f.read()

lines = xml_content.split("\n")
    
tags = pd.read_csv('output4.csv', sep=';')
ec_tags = []
ipc_elements = []
used_tags = []
used_values = []
all_tree = []
#------------------------------------------#


#-----Creating needed lists for the loop----#
for line in tags.values:            #|
    ec_tags.append(line[0])         #| Seperating the EC tags and IPC elements (used for swapping tags)
    ipc_elements.append(line[1])    #|

for e in ipc_elements:                                      #|
    if e != "-":                                            #| The reason for this, beacuse if there is an element which appears more than once in the tree,
        all_tree.append(find_element(e.split('.')[0],""))   #| the program asks the user to choose which one to keep. If i do not put this here, it would ask it everytime.
#------------------------------------------#

#-----Reading input and creating output-----#
formed_xml += lines[0] + "\n" + lines[1] + "\n"     #Keeping the first two lines of the original XML file
lines = xml_content.replace("  ", "").replace("\t","").split("\n") #Removing the unnecessary whitespaces and creating a list of lines
level = 1   #Level of the XML file (used for tabs)

for line in lines[2:]:      #Iterating through the lines of the XML file (skipping the first two lines)
    #----------<row> lines-----------# 
    if line.__eq__("<row>"):    #If the line is a row opening tag, then we need to create the same in the output
        for i in range(0, level):   #|
            formed_xml += "\t"      #| Creating structure with tabs (not commenting this further)
        formed_xml += "<row>\n"
        level += 1          #Increasing the level of the XML file
        used_tags.clear()       #|
        used_values.clear()     #|Clearing the used tags and values for the next row
    #--------------------------------#
        
    #----------</row> lines-----------#    
    elif line.__eq__("</row>"):     #If the line is a row closing tag
        #-----Inserting formatted XML-----#
        used_tree = []      
        for tag in used_tags:                                   #|
            for t in all_tree:                                  #|
                if t.split("/")[-1] == tag.split(".")[0]:       #|Gathering the trees which are used in the row
                    used_tree.append(t)                         #|
        
        used_tree = list(dict.fromkeys(used_tree))              #|IMPORTANT: Removing duplicates from the list & creating alphabetical order
        used_tree = sorted(used_tree)                           #|This way we know if we need to go further in the tree or not
                                                                #|For example: if we have "X.Y" and "X.Z" where x is the same,
                                                                #|we know that we only need to close y and then we can open z immediately, because they have the same parent.
        open_tags = []
        all_tags = []
        all_components = []
        used_tags_start = []
        
        for tag in used_tags:                           
            used_tags_start.append(tag.split(".")[0])
        
        for tag in used_tree:                           #|
            components = tag.split("/")                 #|
            all_tags.append(components)                 #|Seperating the elements of each tree + creating a list of all elements
            for component in components:                #|
                all_components.append(component)        #|
        
        for tag in used_tree:                           #Actually creating the XML lines
            components = tag.split("/")                 #Getting the components of the tree
            for component in components:                    #Iterating through the components
                if component not in open_tags:              #If the component is not in the open tags list, then we need to open it
                    open_tags.append(component)                 #Adding the component to the open tags list
                    
                    for i in range(0, level):               
                        formed_xml += "\t" 
                       
                    if used_tags_start.__contains__(component):     #If there is an attribute paired with a value for the component
                        if all_components.count(component) > 1:     #If the component appears more than once in the tree, a.k.a. it has children. For example: X has attributes: X.y and X.z, but also a child X.W, so we need to open X
                            j = 0
                            formed_xml += f"<{component} "
                            for k in used_tags_start:                                                           #|  
                                if k.__eq__(component):                                                         #| Inserting the attributes and values, to the correct component
                                    formed_xml += f"{used_tags[j].split('.')[1]}=\"{used_values[j]}\" "         #|
                                j += 1
                            formed_xml = formed_xml[:-1]   #Removing the last extra space (for aesthetics only)
                            formed_xml += ">\n"             
                            level += 1
                        else:                       #If the component does not have children, we can close it immediately
                            formed_xml += f"<{component} "
                            j = 0
                            for k in used_tags_start:
                                if k.__eq__(component):
                                    formed_xml += f"{used_tags[j].split('.')[1]}=\"{used_values[j]}\" "
                                j += 1
                            formed_xml = formed_xml[:-1]
                            formed_xml += "/>\n"
                            open_tags.pop()    #Removing the component from the open tags list
                        
                    else:   #If the component does not have attributes, we open it simply
                        formed_xml += f"<{component}>\n"
                        level += 1
            
            if int(used_tree.index(tag)) < len(all_tags)-1:             #If the current tree is not the last one
                while open_tags[-1] not in all_tags[used_tree.index(tag)+1]:        #If the next tree does not contain the last opened tag, we need to close it
                    level -= 1
                    for i in range(0, level):
                        formed_xml += "\t" 
                    formed_xml += f"</{open_tags[-1]}>\n"  #Closing the last opened tag
                    open_tags.pop()        #Removing the last opened tag from the list
                    
            else:
                while len(open_tags) > 0:      #If the current tree is the last one, we need to close all the opened tags
                    level -= 1
                    for i in range(0, level):
                        formed_xml += "\t" 
                    formed_xml += f"</{open_tags[-1]}>\n"
                    open_tags.pop()     
        level -= 1
        for i in range(0, level):
            formed_xml += "\t" 
        formed_xml += "</row>\n"
        #----------------------------------#
    #---------------------------------#
        
    #--------Component rows-----------#
    else:
        old_tag = line.split("<")[1].split(">")[0]  #Extracting the tag (after '<' and before '>')
        if old_tag in ec_tags:
            index = ec_tags.index(old_tag)  #Finding the index of the tag in the list
            new_tag = ipc_elements[index]   #Getting the new tag from the IPC elements list
            if new_tag.__eq__("-"):         #|
                line = ""                   #|If the new tag is "-", then we need to remove the line
            else:                       
                if line.split(">")[1].split("<")[0].__eq__(""):     #|
                    line = ""                                       #|Removing empty values
                else:
                    line = line.replace(old_tag, new_tag)                   #|
                    used_tags.append(new_tag)                               #|If it's not empty, we need to replace the old tag with the new one and store the value and the tag
                    used_values.append(line.split(">")[1].split("<")[0])    #|
        else: 
            line = ""
    #---------------------------------#
    
with open("SAE_IPC_DataModel_formed_v4.xml", "w") as f:
    f.write(formed_xml)
#------------------------------------------#