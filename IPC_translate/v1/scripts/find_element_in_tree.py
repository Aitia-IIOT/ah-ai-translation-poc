#-------Importing JSON library-------#
import json
#-----------------------------------#

#--------Reverse BFS--------#
def findingParent(par_id, data, tree):
    while par_id != None:
        for node in data:
            if node.get("id") == par_id:
                tree.append(node)               
                par_id = node.get("parent")
                break
#----------------------------#    

#--Write the name of the tree--#
def writeName(tree, idx):
    i = 1
    name = ""
    for node in tree:
        name+=(tree[-i].get("name"))
        if i < len(tree):
            i += 1
            name += "/"
    print(f"{idx}: {name}")
#-------------------------------#

#--------Finding the element--------#
def find_element(element, description):
    first = []
    tree = []
    par_id = 0
    with open("auto_tree.json", encoding="utf-8") as f:    #|
        data = json.load(f)                                         #|Loading the nodes from JSON file
        data = data.get("nodes")                                    #|

    for node in data:                                               #|
        if node.get("name") == element:                             #|Finding the first nodes with the same name                  
            first.append(node)                                      #|(Could be more than one)                        
            par_id = node.get("parent")                             #|                       
            
    if len(first) >= 2:           #If there are more than one node with the same name
        answers = []
        i=1
        k=0
        for element in first:
            if isinstance(element.get("parent"), int):              #If the parent is an integer, we can find the parent
                tree.append(element)
                findingParent(element.get("parent"), data, tree)
                answers.append(tree)
                writeName(tree, first.index(element)+1+k)
                tree = []
            elif isinstance(element.get("parent"), list):          #If the parent is a list, we need to find the parent for each element
                l = element.get("parent")
                for way in l:
                    tree.append(element)
                    findingParent(way, data, tree)
                    answers.append(tree)
                    writeName(tree, first.index(element)+1+k)
                    k+=1
                    tree = []
                    
        #input_idx = int(input("Which one is the correct one? "))   #Asking the user to choose the correct one
        input_idx = 1
        name = ""
        for node in answers[input_idx-1]:
            name+=(answers[input_idx-1][-i].get("name"))
            if i < len(answers[input_idx-1]):
                i += 1
                name += "/"
        #print(f"Chosen: {name}")
        return name
                            
    elif len(first) == 1:     #If there is only one node with the same name
        k=0
        answers = []
        if isinstance(first[0].get("parent"), list):    #If the parent is a list, we need to find the parent for each element
            for way in first[0].get("parent"):
                tree.append(first[0])
                findingParent(way, data, tree)
                answers.append(tree)
                writeName(tree, 1+k)
                k+=1
                tree = []

            input_idx = 1
            #input_idx = int(input("Which one is the correct one? "))    #Asking the user to choose the correct one
            name = ""
            i=1
            for node in answers[input_idx-1]:
                name+=(answers[input_idx-1][-i].get("name"))
                if i < len(answers[input_idx-1]):
                    i += 1
                    name += "/"
            #print(f"Chosen: {name}")
            return name
            
        else:  #If the parent is an integer, we can find the parent, no need to choose
            tree.append(first[0])
            findingParent(par_id, data, tree)
            name = ""
            i = 1
            for node in tree:
                name+=(tree[-i].get("name"))
                if i < len(tree):
                    i += 1
                    name += "/"
            #print(f"Chosen: {name}")
            return name 
    
    else:   #If there is no node with the same name just return an empty string
        print("No element found")
        return ""
#---------------------------------#

if __name__ == "__main__":                      #|
    print(find_element("Impedance", ""))      #|Testing the function