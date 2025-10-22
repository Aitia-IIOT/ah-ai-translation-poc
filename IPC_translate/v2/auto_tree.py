import os


def auto_tree():
    with open('IPC-2581C.xsd', 'r') as f:
        data = f.read()
        
    lines = []
    ipc_class_names = []
    ipc_elements = []
    left = []
    right = []
    sublist = []
    root = ""
    req = ""
    element_etype_list=[]

    for line in data.split("\n"):
        lvl = line.count("\t")
        line = line.replace("\t", "").replace("xsd:", "")
        lines.append((line, lvl))

    curr_element = ""
    elements = ""
    sub = []
    substitutionGroups = []
    substitutions = []
    sg = []

    for line in lines:
        if line[0].__contains__("<element") and line[1] == 1:
            name = line[0].split(" ")[1].replace("name=", "").replace('"', "").replace(">", "").replace("/", "")
            type = line[0].split(" ")[2].replace("type=", "").replace('"', "").replace(">", "").replace("/", "")
            truple = (name, type)
            element_etype_list.append(truple)

                
        if line[0].__contains__("<complexType") and line[1] == 1:
            idx = [element for element in element_etype_list if element[1] == line[0].split(" ")[1].replace("name=", "").replace('"', "").replace(">", "").replace("/", "")]
            sub = idx
            
        if line[0].__contains__("substitutionGroup"):
                name = line[0].split(" ")[1].replace("name=", "").replace('"', "").replace(">", "").replace("/", "")
                subgroup = line[0].split(" ")[3].replace("substitutionGroup=", "").replace('"', "").replace(">", "").replace("/", "")
                substitutionGroups.append(name)
                substitutions.append([name,subgroup])
                sg.append(subgroup)
            
        
        if line[0].__contains__("<element") and line[1] == 3:
            name = line[0].split(" ")[1].replace("ref=", "").replace('"', "").replace(">", "").replace("/", "")
            if sg.__contains__(name):
                for s in substitutions:
                    if s[1] == name:
                        elements += s[0] + ", "
                        right.append(s[0])
                        if len(line[0].split(" "))<3 or line[0].__contains__("minOccurs=\"1\"") or (line[0].__contains__("maxOccurs") and not line[0].__contains__("minOccurs")):
                            for s in sub:
                                req += s[0] + "." + name + "\n"
            else:
                elements += name + ", "
                if len(line[0].split(" "))<3 or line[0].__contains__("minOccurs=\"1\"") or (line[0].__contains__("maxOccurs") and not line[0].__contains__("minOccurs")):
                    for s in sub:
                        req += s[0] + "." + name + "\n"
                    
                
            
        if line[0].__contains__("</sequence>") and line[1] == 2:
            if sub != "":
                ipc_elements.append((sub[0], elements[:-2]))
            if sub != "":
                for s in sub:
                    for e in elements[:-2].split(", "):
                        sublist.append(s[0]+"."+e)
            elements = ""
            curr_element = ""
            sub = ""


    for e in ipc_elements:
        for i in e[1].split(", "):
            right.append(i)
        left.append(e[0][0])


    for s in substitutionGroups:
        if s in left:
            left.remove(s)
        
    #print(sublist)
    #sublist = sorted(sublist)

    #print(sublist)

    right = list(dict.fromkeys(right))
    for l in left:
        if not right.__contains__(l):
            root = l
            

    

    nr = 1
    curr_parent_id = 1
    curr_parent = root
    curr_element = root
    tree_output = "{\n\t\"nodes\":[\n"
    tree_output += "\t\t{\"id\": "+str(nr)+", \"name\": \""+root+"\", \"parent\": null},\n"

    all_star = []
    ids = []
    ids.append((root,1))

    for e in ipc_elements:
        for i in e[1].split(", "):
            all_star.append(e[0][0]+"."+i)


    print(all_star)

    all_star2 = all_star.copy()

    undiscovered_children = []

    while len(all_star) > 0:
        for i in all_star:
            if i.split(".")[0] == curr_element:
                if i.split(".")[0] == curr_element:
                    nr += 1
                    for id in ids:
                        if id[0] == curr_element:
                            curr_parent_id = id[1]
                            
                    tree_output += "\t\t{\"id\": "+str(nr)+", \"name\": \""+i.split(".")[1]+"\", \"parent\": "+str(curr_parent_id)+"},\n"
                    undiscovered_children.append(i.split(".")[1])
                    ids.append((i.split(".")[1], nr))
        for i in undiscovered_children:
            if all_star.__contains__(curr_element+"."+i):
                all_star.remove(curr_element+"."+i)
        if len(undiscovered_children) > 0:
            curr_element = undiscovered_children[0]
            undiscovered_children.pop(0)
        else:    
            all_star = []
        
          


    parent_children = {}
    for entry in all_star2:
        parent, child = entry.split(".")
        if parent not in parent_children:
            parent_children[parent] = []
        parent_children[parent].append(child)

    global custom_alphabet
    custom_alphabet = ""

    def dfs_traverse(node, path):
        global custom_alphabet
        
        # Add current path to alphabet
        custom_alphabet += path + "\n"
        
        # Recursively traverse children in sorted order
        if node in parent_children:
            for child in parent_children[node]:
                child_path = path + "/" + child
                dfs_traverse(child, child_path)

    # Start DFS from root
    dfs_traverse(root, root)

    # Remove any empty lines and duplicates while preserving order
    lines = custom_alphabet.strip().split('\n')
    seen = set()
    unique_lines = []
    for line in lines:
        if line and line not in seen:
            seen.add(line)
            unique_lines.append(line)

    custom_alphabet = '\n'.join(unique_lines)
    
    first_layer_elements = []
    if root in parent_children:
        first_layer_elements = parent_children[root]

    # Write first layer elements to file
    first_layer_output = '\n'.join(first_layer_elements)
    with open('variables/first_layer_elements.txt', 'w') as f:
        f.write(first_layer_output)

    # Output the result
    #print(custom_alphabet)
    with open('variables/custom_alphabet.txt', 'w') as f:
        f.write(custom_alphabet[:-1])

    tree_output = tree_output[:-2] + "\n\t]\n}"

    with open('variables/auto_tree.json', 'w') as f:
        f.write(tree_output)

    with open('variables/req_class.txt', 'w') as f:
        f.write(req)
        
    os.makedirs("variables/sections", exist_ok=True)

    # Initialize section dictionaries
    sections = {}
    for element in first_layer_elements:
        sections[element] = []

    # Separate alphabet lines by first layer elements
    for line in custom_alphabet.split("\n"):
        if line.strip():  # Skip empty lines
            path_parts = line.split("/")
            
            # For root line, skip it or handle separately
            if len(path_parts) == 1:
                continue
                
            # Get the first layer element (second part after root)
            if len(path_parts) >= 2:
                first_layer = path_parts[1]
                
                # Check if this line belongs to any first layer element
                if first_layer in first_layer_elements:
                    sections[first_layer].append(line)

    # Write each section to its own file
    for element in first_layer_elements:
        section_content = '\n'.join(sections[element])
        with open(f"variables/sections/{element}.txt", 'w') as f:
            f.write(section_content)
                    

if __name__ == "__main__":
    auto_tree()
