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

for line in data.split("\n"):
    lvl = line.count("\t")
    line = line.replace("\t", "").replace("xsd:", "")
    lines.append((line, lvl))

curr_element = ""
elements = ""
sub = ""

for line in lines:
    '''if line[0].__contains__("<complexType") and line[1] == 1:
        line_sep = line[0].split(" ")
        name = line_sep[1].replace("name=", "").replace('"', "").replace(">", "").replace("Type", "")
        ipc_class_names.append(name)
        curr_element = name'''
            
    if line[0].__contains__("<element") and line[1] == 1:
        if line[0].__contains__("substitutionGroup"):
            subgroup = line[0].split(" ")[3].replace("substitutionGroup=", "").replace('"', "").replace(">", "").replace("/", "")
            name = line[0].split(" ")[1].replace("name=", "").replace('"', "").replace(">", "").replace("/", "")
            sublist.append(subgroup+"."+name)
            sub = name
        else:
            name = line[0].split(" ")[1].replace("name=", "").replace('"', "").replace(">", "").replace("/", "")
            curr_element = name
        
    
    if line[0].__contains__("<element") and line[1] == 3:
        name = line[0].split(" ")[1].replace("ref=", "").replace('"', "").replace(">", "").replace("/", "")
        right.append(name)
        elements += name + ", "
        
    if line[0].__contains__("</sequence>") and line[1] == 2:
        if curr_element != "":
            ipc_elements.append((curr_element, elements[:-2]))
        if sub != "":
            for e in elements[:-2].split(", "):
                sublist.append(sub+"."+e)
        elements = ""
        curr_element = ""
        sub = ""
    
ipc_elements = sorted(ipc_elements)

for e in ipc_elements:
    for i in e[1].split(", "):
        right.append(i)
    left.append(e[0])
    
print(sublist)
sublist = sorted(sublist)

print(sublist)

'''for s in sublist:
    right.append(s[0])
    for i in s[1].split(", "):
        right.append(i)''' 
right = list(dict.fromkeys(right))
for l in left:
    if not right.__contains__(l):
        root = l
        break


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
        all_star.append(e[0]+"."+i)

for s in sublist:
    all_star.append(s)

all_star = sorted(all_star)

undiscovered_children = []
#print(all_star)

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
          
tree_output = tree_output[:-2] + "\n\t]\n}"

with open('auto_tree.json', 'w') as f:
    f.write(tree_output)

        