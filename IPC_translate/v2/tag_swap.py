#----------Importing libraries--------------#
import pandas as pd
import sys
import time
sys.setrecursionlimit(2000)

#------------------------------------------#

def translate(filename):

    start = time.time()

    #-----Creating variables and reading data-----#
    xml_content = ""
    output_xml = ""
    formed_xml = ""

    # Read the XML content
    with open(f"input/{filename}.xml", "r") as f:
        xml_content = f.read()

    # Read auto variables
    with open("variables/auto_variables.txt", "r") as f:
        data = f.read().split("\n")

    # Read custom alphabet
    with open("variables/custom_alphabet.txt", "r") as f:
        cst_alph = f.read().split("\n")

    ipc_elements = []
    els = []

    # Process auto variables
    for line in data:
        if "req" in line:
            els.append(line.split(" × ")[0])
            ipc_elements.append(line.split(" × ")[0])

    lines = xml_content.split("\n")

    # Read tags from CSV
    tags = pd.read_csv('mapping_table/EC_IPC.csv', sep=';')
    ec_tags = []

    # Read required classes
    with open("variables/req_class.txt", "r") as f:
        req = f.read().split("\n")
        req2 =req.copy()
        req_class = [c.split(".")[0] for c in req if c != ""]

    used_tags = []
    used_values = []
    all_tree = []
    used_ipc_elements = []
    #------------------------------------------#

    #-----Creating needed lists for the loop----#
    for line in tags.values:
        ec_tags.append(line[0])
        ipc_elements.append(line[1])
        used_ipc_elements.append(line[1])

    '''for line in req_class:
        if line:
            ipc_elements.append(line.split(".")[1])'''

    # Build the tree
    for e in ipc_elements:
        if e != "-":
            try:
                all_tree.append(e)
            except Exception as ex:
                print(ex)



    #------------------------------------------#

    #-----Reading input and creating output-----#
    formed_xml += "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"  # Add XML declaration
    lines = xml_content.replace("  ", "").replace("\t", "").split("\n")  # Removing unnecessary whitespaces
    level = 0  # Level of the XML file (used for tabs)

    # Precompute tree map for faster lookups
    tree_map = {t for t in all_tree}
    used_tree = []


    for line in lines[1:]:  # Iterating through the lines of the XML file (skipping the first two lines)
        #----------<row> lines-----------#
        if line == "<row>":  # If the line is a row opening tag
            used_tags.clear()
            used_values.clear()
            req=req2.copy()
        #--------------------------------#

        #----------</row> lines-----------#
        elif line == "</row>":  # If the line is a row closing tag        #-----Inserting formatted XML-----#
            print("Processing row...")
            print(f"Used tags: {used_tags}")
            print(f"Used values: {used_values}")
            
            # Only include paths for elements that were actually used
            used_tree = []
            
            # Extract element names from used_tags (handle both full paths and element.attribute format)
            used_elements = set()
            for tag in used_tags:
                if "/" in tag:
                    # Full path format: extract element name
                    element_name = tag.split("/")[-1].split(".")[0]
                else:
                    # element.attribute format
                    element_name = tag.split(".")[0]
                used_elements.add(element_name)
            
            # Find matching paths from all_tree for used elements
            for path in all_tree:
                path_element = path.split("/")[-1].split(".")[0] if "." in path.split("/")[-1] else path.split("/")[-1]
                if path_element in used_elements:
                    # Extract clean path without attributes
                    if "." in path.split("/")[-1]:
                        path_parts = path.split("/")
                        path_parts[-1] = path_parts[-1].split(".")[0]
                        clean_path = "/".join(path_parts)
                    else:
                        clean_path = path
                    
                    if clean_path not in used_tree:
                        used_tree.append(clean_path)
            
            print(f"Used tree after filtering: {used_tree}")
                       
            open_tags = []
            all_tags = []
            all_components = []
            used_tags_start = [tag.split(".")[0] if "." in tag else tag.split("/")[-1].split(".")[0] if "/" in tag else tag for tag in used_tags]
            req_tags_start = [e.split(".")[0] for e in els]
            
            for tag in used_tree:
                components = tag.split("/")
                all_tags.append(components)
                all_components.extend(components)
            
            # Initialize with empty list and use a flag to control the loop
            curr_req_class = []
            continue_processing = True
            while continue_processing:
                newly_added_to_curr_req_class = False
                temp_curr_req_class = [] # Use a temporary list for new items in this iteration
                for tree in used_tree:
                    components = tree.split("/")
                    for comp in components:
                        if comp in req_class:
                            # Use a copy of req to avoid modifying while iterating
                            req_copy = req.copy()
                            for r in req_copy:
                                if comp == r.split(".")[0]:
                                    idx = components.index(comp)
                                    # Renamed 'component' to 'c_item' in the generator
                                    path_prefix = "".join(c_item + "/" for c_item in components[:idx + 1])
                                    new_element = path_prefix + r.split(".")[1]
                                    if new_element not in used_tree and new_element not in temp_curr_req_class : # Avoid adding if already processed or in current batch
                                        temp_curr_req_class.append(new_element)
                                        newly_added_to_curr_req_class = True
                                    if r in req:  # Check if still in list before removing
                                        req.remove(r)
                
                if newly_added_to_curr_req_class:
                    for item in temp_curr_req_class:
                        if item not in used_tree: # Double check before adding to used_tree
                            used_tree.append(item)
                            # also update all_tags and all_components if necessary
                            new_components = item.split("/")
                            all_tags.append(new_components)
                            all_components.extend(new_components)
                else:
                    continue_processing = False # No new elements found in this pass

        # Sort the tree based on custom alphabet
            def longest_common_prefix(s1, s2):
                s1_parts = s1.split("/")
                s2_parts = s2.split("/")
                common = []
                for part1, part2 in zip(s1_parts, s2_parts):
                    if part1 == part2:
                        common.append(part1)
                    else:
                        break
                return "/".join(common)

            tree_order = []
            for tag in used_tree:
                if tag in cst_alph:
                    idx = cst_alph.index(tag)
                    tree_order.append([tag, idx])
                else:
                    # Find the best position based on hierarchical structure
                    best_idx = len(cst_alph)  # Default to end if no good match found
                    
                    # Try to find parent path in alphabet
                    tag_parts = tag.split("/")
                    for i in range(len(tag_parts) - 1, 0, -1):
                        parent_path = "/".join(tag_parts[:i])
                        if parent_path in cst_alph:
                            parent_idx = cst_alph.index(parent_path)
                            # Place after parent but before next major section
                            best_idx = parent_idx + 1
                            break
                    
                    # If still no good position, try longest common prefix
                    if best_idx == len(cst_alph):
                        longest_match = max(cst_alph, key=lambda x: len(longest_common_prefix(x, tag)))
                        lm_idx = cst_alph.index(longest_match)
                        # Add small offset to avoid exact index collision
                        best_idx = lm_idx + 0.5
                    
                    tree_order.append([tag, best_idx])

            # Sort by index, then by hierarchical depth (shorter paths first), then alphabetically
            tree_order.sort(key=lambda x: (x[1], len(x[0].split("/")), x[0]))
            used_tree = [t[0] for t in tree_order]                 
                                

            seen = set()
            used_tree = [x for x in used_tree if not (x in seen or seen.add(x))]
            
            all_tags = []
            for tag in used_tree:
                components = tag.split("/")
                blub = []
                for c in components:
                        blub.append(c)
                all_tags.append(blub)
                    
            
            seen = set()
            all_tags = [tuple(x) for x in all_tags]  # Convert lists to tuples
            all_tags = [x for x in all_tags if not (x in seen or seen.add(x))]
            
            #print("Used tree: ", used_tree)
            #print("All tags: ", all_tags)
            #print(req_tags_start)
            
            loop_start = time.time()
            for tag in used_tree:
                components = tag.split("/")
                for component in components:
                    if component not in open_tags:
                        open_tags.append(component)
                        formed_xml += "\t" * level
                        if component != components[-1]:
                            formed_xml += f"<{component}"
                            if component in used_tags_start:
                                formed_xml += " ".join(
                                    f' {used_tags[j].split(".")[1]}="{used_values[j]}"'
                                    for j, k in enumerate(used_tags_start) if k == component
                                )
                            elif component in req_tags_start:
                                formed_xml += " ".join(
                                    f' {els[j].split(".")[1]}=""'
                                    for j, k in enumerate(req_tags_start) if k == component
                                )
                            formed_xml += ">\n"
                            level += 1
                        else:
                            if used_tree.index(tag) < len(used_tree) - 1 and component in used_tree[used_tree.index(tag) + 1].split("/"):
                                formed_xml += f"<{component}"
                                if component in used_tags_start:
                                    formed_xml += " ".join(
                                        f' {used_tags[j].split(".")[1]}="{used_values[j]}"'
                                        for j, k in enumerate(used_tags_start) if k == component
                                    )
                                elif component in req_tags_start:
                                    formed_xml += " ".join(
                                        f' {els[j].split(".")[1]}=""'
                                        for j, k in enumerate(req_tags_start) if k == component
                                    )
                                formed_xml += ">\n"
                                level += 1
                            elif used_tree[used_tree.index(tag) - 1] != tag:
                                formed_xml += f"<{component}"
                                if component in used_tags_start:
                                    formed_xml += " ".join(
                                        f' {used_tags[j].split(".")[1]}="{used_values[j]}"'
                                        for j, k in enumerate(used_tags_start) if k == component
                                    )
                                elif component in req_tags_start:
                                    formed_xml += " ".join(
                                        f' {els[j].split(".")[1]}=""'
                                        for j, k in enumerate(req_tags_start) if k == component
                                    )
                                formed_xml += "/>\n"
                                open_tags.pop()
                                
                #print("Time taken for tag processing: ", time.time() - loop_start)
                        
                        
                if used_tree.index(tag) < len(all_tags) - 1:
                    # Close tags that are not part of the next tag's path
                    while len(open_tags) > 0 and (open_tags[-1] not in all_tags[used_tree.index(tag) + 1]):
                        level -= 1
                        formed_xml += "\t" * level + f"</{open_tags.pop()}>\n"
                else:
                    while len(open_tags) > 0:
                        #print("While: "+str(len(open_tags)))
                        level -= 1
                        formed_xml += "\t" * level + f"</{open_tags.pop()}>\n"
            level = 1
            #formed_xml += "\t" * level + "</row>\n"
            #print("Time taken for section: ", (time.time() - section_start)*1000, " milliseconds")
        #--------------------------------#
        elif line == "":
            continue
        #--------Component rows-----------#
        
        else:
            old_tag = line.split("<")[1].split(">")[0]
            if old_tag in ec_tags:
                index = ec_tags.index(old_tag)
                new_tag = used_ipc_elements[index]
                if new_tag == "-":
                    line = ""
                else:
                    if line.split(">")[1].split("<")[0] == "":
                        line = ""
                    else:
                        # Handle tag replacement properly based on format
                        if "/" in new_tag:
                            # Full path format - extract element name and attribute
                            if "." in new_tag.split("/")[-1]:
                                element_name = new_tag.split("/")[-1].split(".")[0]
                                attribute_name = new_tag.split("/")[-1].split(".")[1]
                                line = line.replace(old_tag, element_name)
                                used_tags.append(f"{element_name}.{attribute_name}")
                            else:
                                element_name = new_tag.split("/")[-1]
                                line = line.replace(old_tag, element_name)
                                used_tags.append(element_name)
                        else:
                            # Simple element or element.attribute format
                            if "." in new_tag:
                                element_name = new_tag.split(".")[0]
                                line = line.replace(old_tag, element_name)
                            else:
                                line = line.replace(old_tag, new_tag)
                            used_tags.append(new_tag)
                        
                        used_values.append(line.split(">")[1].split("<")[0])
                        print(f"Processed: {old_tag} -> {new_tag}, element in XML: {element_name if 'element_name' in locals() else new_tag}")
            else:
                line = ""
        #---------------------------------#
    #formed_xml += "</row>\n"
    # Fixing the IPC tags by the description - only output the properly structured content
    formed_xml_ipc_fixed = ""

    # Find the IPC-2581 section and only output that
    lines = formed_xml.split("\n")
    found_ipc = False
    
    for i, line in enumerate(lines):
        if line.__contains__("<row>") or line.__contains__("</row>") or line == "":
            continue
        
        if "<IPC-2581" in line:
            formed_xml_ipc_fixed += "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            formed_xml_ipc_fixed += "<IPC-2581 xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns=\"http://webstds.ipc.org/2581\" revision=\"C\">\n"
            found_ipc = True
        elif found_ipc:
            # Only add lines after we found IPC-2581
            formed_xml_ipc_fixed += line + "\n"

    # Write the final output
    with open(f"output/{filename}.xml", "w") as f:
        f.write(formed_xml_ipc_fixed)
        
    #print("Time taken: ", time.time() - start)
    
    
if __name__ == "__main__":
    import sys
    
    # Check if filename parameter is provided
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        try:
            translate(filename)
        except Exception as e:
            print(f"❌ Error during translation: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("Usage: python tag_swap.py <filename>")
        print("Example: python tag_swap.py input1")
        sys.exit(1)
    