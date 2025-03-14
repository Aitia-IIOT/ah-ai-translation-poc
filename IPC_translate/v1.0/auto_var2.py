


with open('IPC-2581C.xsd', 'r') as f:
    data = f.read()
    
lines = []
ipc_class_names = []
cmplx_classes = []
ipc_elements = []
not_basic_types = []
nb = []

for line in data.split("\n"):
    lvl = line.count("\t")
    line = line.replace("\t", "").replace("xsd:", "")
    lines.append((line, lvl))

type = ""
basic_type = ""
enum = ""
nr_restrictions = ""
pattern = ""
class_name = ""

for line in lines:
    if line[0].__contains__("<element") and line[1] == 1:
        line_sep = line[0].split(" ")
        name = line_sep[1].replace("name=", "").replace('"', "")
        if line_sep[2].__contains__("type"):
            type = line_sep[2].replace("type=", "").replace('"', "").replace("/", "").replace(">", "")
            ipc_class_names.append((name, type))
            cmplx_classes.append((name,type))
        else:
            ipc_class_names.append((name, None))
    if line[0].__contains__("<complexType") and line[1] == 1:
        type = line[0].split(" ")[1].replace("name=", "").replace('"', "").replace(">", "")
        for cls in cmplx_classes:
            if type==cls[1]:
                class_name = cls[0]
                break
    if line[0].__contains__("<attribute") and line[1] == 2:
        line_sep = line[0].split(" ")
        name = line_sep[1].replace("name=", "").replace('"', "")
        type = line_sep[2].replace("type=", "").replace('"', "").replace("/", "").replace(">", "")
        if not nb.__contains__(type):
            ipc_elements.append((class_name+"."+name+" | "+type))
        else:
            idx = nb.index(type)
            t = not_basic_types[idx]
            ipc_elements.append((class_name+"."+name+" | "+type+" { "+t[1]+", "+t[2]+" }"))
        
    if line[0].__contains__("<simpleType") and line[1] == 1:
        type = line[0].split(" ")[1].replace("name=", "").replace('"', "").replace(">", "")
        basic_type = lines[lines.index(line)+1][0].replace("<restriction base=", "").replace('"', "").replace(">", "")
    if line[0].__contains__("<enumeration") and line[1] == 3:
        enum += line[0].split(" ")[1].replace("value=", "").replace('"', "").replace("/>", "") + ", "
    if line[0].__contains__("<pattern") and line[1] == 3:
        pattern += line[0].split(" ")[1].replace("value=", "").replace('"', "")
    if ( line[0].__contains__("<min") or line[0].__contains__("<max") or line[0].__contains__("<total") or line[0].__contains__("<fraction") ) and line[1] == 3:
        nr_restrictions += line[0].replace("<", "").replace("/>", "").replace("value", "") + ", "
    if line[0].__contains__("</simpleType>"):
        if enum != "":
            not_basic_types.append((type, basic_type, "ENUM VALUES: " + enum[:-2]))
        elif nr_restrictions != "":
            not_basic_types.append((type, basic_type, "RESTRICTIONS: " + nr_restrictions[:-2]))
        elif pattern != "":
            not_basic_types.append((type, basic_type, "PATTERN: " + pattern))
        nb.append(type)
        type = ""
        basic_type = ""
        enum = ""
        nr_restrictions = ""
        pattern = ""
    
for type in not_basic_types:
    print(type)
  
  
for element in ipc_elements:
    print(element)
    
    
ipc_elements = sorted(ipc_elements)

output = ""        
for element in ipc_elements:
    output += element + "\n"
    
with open('variables/auto_variables.txt', 'w') as f:
    f.write(output[:-1])       
        
    