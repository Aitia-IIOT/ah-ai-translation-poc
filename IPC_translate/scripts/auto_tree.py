import json


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


for line in lines:
    '''if line[0].__contains__("<complexType") and line[1] == 1:
        line_sep = line[0].split(" ")
        name = line_sep[1].replace("name=", "").replace('"', "").replace(">", "").replace("Type", "")
        ipc_class_names.append(name)
        curr_element = name'''
            
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

'''for s in sublist:
    right.append(s[0])
    for i in s[1].split(", "):
        right.append(i)''' 
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

with open('auto_tree.json', 'w') as f:
    f.write(tree_output)

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
    #print(undiscovered_children)
    if len(undiscovered_children) > 0:
        curr_element = undiscovered_children[0]
        undiscovered_children.pop(0)
    else:
        #print(all_star)
        all_star = []
    #print(tree_output)
nr = 1
curr_parent_id = 1
curr_parent = root
curr_element = root   
ids = []
ids.append((root,1)) 

custom_alphabet = ""

stack = [(curr_element, curr_element)]  # (node, full_path)
ids = [(curr_element, 0)]
nr = 0

while stack:
    curr_element, curr_path = stack.pop()

    # Visit the current node
    custom_alphabet += curr_path + "\n"

    # Find children of the current node
    children = []
    for entry in all_star2[:]:
        parent, child = entry.split(".")
        if parent == curr_element:
            nr += 1
            full_path = curr_path + "/" + child
            ids.append((child, nr))
            children.append((child, full_path))
            all_star2.remove(entry)  # Remove processed child

    # Push children onto the stack in reverse order for DFS
    for child, full_path in reversed(children):
        stack.append((child, full_path))

ca = list(dict.fromkeys(custom_alphabet.split("\n")))
custom_alphabet = ""
for c in ca:
    custom_alphabet += c + "\n"

# Output the result
#print(custom_alphabet)
with open('custom_alphabet.txt', 'w') as f:
    f.write(custom_alphabet[:-1])



tree_output = tree_output[:-2] + "\n\t]\n}"

with open('auto_tree.json', 'w') as f:
    f.write(tree_output)
    
with open('req_class.txt', 'w') as f:
    f.write(req)

        