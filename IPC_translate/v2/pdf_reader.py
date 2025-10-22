import pdfplumber
import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import re

def pdf_reader():
    if not len(os.listdir("expandedRag")) == 8:
        #Insert key for OpenAI
        ef = OpenAIEmbeddings(api_key="xyz")

        chapters = []
        elements = []

        def clean_cell(cell):
            """Clean individual cell content"""
            if cell is None:
                return ""
            if not isinstance(cell, str):
                return str(cell).strip()
            
            # Remove newlines and normalize whitespace
            cleaned = re.sub(r'\s+', ' ', cell.replace('\n', ' ').replace('\r', ''))
            # Remove special characters that cause issues
            cleaned = cleaned.replace('\\n', '').replace('�', '').strip()
            return cleaned

        def clean_and_validate_table(table):
            """Improved table cleaning with validation"""
            if not table or len(table) == 0:
                return []
            
            cleaned_table = []
            for row in table:
                if not row:
                    continue
                
                # Clean each cell in the row
                cleaned_row = [clean_cell(cell) for cell in row]
                
                # Skip rows that are entirely empty
                if not any(cell.strip() for cell in cleaned_row if cell):
                    continue
                    
                cleaned_table.append(cleaned_row)
            
            return cleaned_table

        def is_valid_element_row(row):
            """Check if a row represents a valid element definition"""
            if not row or len(row) < 3:
                return False
            
            # Must have occurrence indicator
            has_occurrence = any(indicator in str(cell) for cell in row 
                            for indicator in ["0-1", "0-n", "1-1", "1-n"])
            
            # First cell should be a valid element name
            first_cell = str(row[0]).strip()
            has_valid_name = (len(first_cell) > 0 and 
                            not first_cell.lower() in ['element', 'name', 'occurrence', 'description'])
            
            return has_occurrence and has_valid_name

        def extract_tables_improved(page):
            """Extract tables with multiple strategies to handle overlapping tables"""
            tables = []
            
            # Strategy 1: Standard extraction
            try:
                standard_tables = page.extract_tables()
                if standard_tables:
                    tables.extend(standard_tables)
            except Exception as e:
                print(f"Standard table extraction failed: {e}")
            
            # Strategy 2: With different settings for overlapping tables
            try:
                overlap_tables = page.extract_tables(
                    table_settings={
                        "vertical_strategy": "lines_strict",
                        "horizontal_strategy": "lines_strict",
                        "snap_tolerance": 3,
                        "join_tolerance": 3
                    }
                )
                if overlap_tables:
                    # Add tables that weren't found in standard extraction
                    for table in overlap_tables:
                        if table not in tables:
                            tables.append(table)
            except Exception as e:
                print(f"Overlap table extraction failed: {e}")
            
            # Strategy 3: Text-based extraction for merged cells
            try:
                text_lines = page.extract_text().split('\n')
                text_table = []
                for line in text_lines:
                    # Look for lines that might be table rows
                    if any(indicator in line for indicator in ["0-1", "0-n", "1-1", "1-n"]):
                        # Split by multiple spaces or tabs
                        cells = re.split(r'\s{2,}|\t+', line.strip())
                        if len(cells) >= 2:
                            text_table.append(cells)
                
                if text_table:
                    tables.append(text_table)
            except Exception as e:
                print(f"Text-based extraction failed: {e}")
            
            return tables

        with pdfplumber.open("./IPC-2581C.pdf") as pdf:
            pagenr = 1
            chaptername = ""
            for page in pdf.pages:        
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if (row.__contains__("0-1") or row.__contains__("0-n") or row.__contains__("1-1") or row.__contains__("1-n")):
                            #if row[0] is None:
                            for cell in row:
                                if cell is None or not isinstance(cell, str):
                                    cell2 = ""
                                    row[row.index(cell)] = cell2
                                else:
                                    for char in cell:
                                        if char == "\\":
                                            if cell[cell.index(char)+1] == "n":
                                                cell = cell.replace(char+1, "")
                                                cell = cell.replace(char, "")
                            cleaned_row = [cell.strip() for cell in row if isinstance(cell, str) and cell.strip() != ""]
                            if (table.index(row) == 3 or table.index(row) == 2 or table.index(row) == 0) and row[0][0].isupper():
                                chaptername = cleaned_row[0]
                                print(chaptername)
                            else:
                                print(chaptername+"."+cleaned_row[0])
                                if cleaned_row[0][0].islower() or cleaned_row[0][0] == 'O':
                                    print("ADDED: "+chaptername+"."+cleaned_row[0])
                                    element_name = cleaned_row[0]
                                    desc = cleaned_row[2]
                                    elements.append((chaptername+"."+element_name, desc))


        for element in elements:
            print(element)

        cleaned_elements = []

        for element in elements:
            cleaned_element = []
            for i in range(0, len(element)):
                if element[i].__contains__("\n"):
                    elem = element[i].replace("\n", "").replace("�", "")
                else:
                    elem = element[i]
                cleaned_element.append(elem)
            cleaned_elements.append(cleaned_element)

        with open("variables/auto_variables.txt", "r", encoding="utf-8") as f:
            data = f.read()

        richer_data = []
        
        # Debug: Print sample cleaned_elements and auto_variables format
        print("\n=== DEBUG: Checking format compatibility ===")
        print(f"Total cleaned_elements from PDF: {len(cleaned_elements)}")
        if cleaned_elements:
            print(f"Sample PDF elements (first 5):")
            for elem in cleaned_elements[:5]:
                print(f"  {elem[0]}")
        
        auto_var_lines = [line.strip() for line in data.split("\n") if line.strip()]
        print(f"\nTotal auto_variables lines: {len(auto_var_lines)}")
        if auto_var_lines:
            print(f"Sample auto_variables (first 5):")
            for line in auto_var_lines[:5]:
                print(f"  {line.split(' × ')[0] if ' × ' in line else line}")
        print("=== END DEBUG ===\n")

        # Match by attribute name (after the dot) since PDF has element names but auto_var has ComplexType names
        matched_count = 0
        unmatched_elements = []
        
        for element in cleaned_elements:
            # Extract attribute name from PDF element (e.g., "IPC-2581.revision" -> "revision")
            if "." in element[0]:
                pdf_element_name = element[0].split(".")[0]
                pdf_attribute = element[0].split(".")[-1]
                
                matched = False
                # Look for matching attribute in auto_variables
                for line in data.split("\n"):
                    if line.strip():
                        # Extract ComplexType and attribute from auto_variables line
                        # Format: "ComplexType.attribute × type × default..."
                        if " × " in line:
                            auto_var_full = line.split(" × ")[0].strip()
                            if "." in auto_var_full:
                                auto_attr = auto_var_full.split(".")[-1]
                                
                                # Match by attribute name
                                if auto_attr == pdf_attribute:
                                    enriched_line = line.strip() + " × " + element[1]
                                    print(f"✓ Matched: {element[0]} -> {auto_var_full}")
                                    richer_data.append(enriched_line)
                                    matched = True
                                    matched_count += 1
                                    break
                
                if not matched:
                    unmatched_elements.append(element[0])
            else:
                unmatched_elements.append(element[0])
        
        print(f"\n=== Matching Results ===")
        print(f"Matched: {matched_count}/{len(cleaned_elements)}")
        print(f"Unmatched: {len(unmatched_elements)}")
        if unmatched_elements and len(unmatched_elements) <= 10:
            print(f"Unmatched elements: {unmatched_elements}")
        print("=== END ===\n")

        try:
            richer_txt = ""
            richer_data = sorted(richer_data)
            for line in richer_data:
                richer_txt += line
            with open("variables/rich_auto_variables.txt", "w", encoding="utf-8") as f:
                f.write(richer_txt)
                
            db_data = []

            with open("IPC-2581C_elements.txt", "w", encoding="utf-8") as f:
                for element in cleaned_elements:
                    f.write(element[0] + " × " + element[1] + "\n")
                    db_data.append(element[0] + " × " + element[1] + "\n")
                    
            db_names = set()

            for element in db_data:
                if element.split(" × ")[0].split('.')[0] not in db_names:
                    db_names.add(element.split(" × ")[0].split(".")[0])
                    
            for name in db_names:
                content=[]
                for element in richer_data:
                    if element.split(" × ")[0].split(".")[0] == name:
                        content.append(element)

            print(len(richer_data))
            print("\n\n\n\n-----\n\n\n\n")

            with open("variables/custom_alphabet.txt", "r", encoding="utf-8") as f:
                alphabet_paths = [line.strip() for line in f.readlines() if line.strip()]
            
            # Create path_data by matching alphabet paths with richer_data descriptions
            path_data = []

            

            for path in alphabet_paths:
                # Get the last element from the path (e.g., "Color" from "IPC-2581/Content/DictionaryColor/EntryColor/Color")
                path_element = path.split("/")[-1]
                
                # Find matching richer_data elements
                for element in richer_data:
                    element_name = element.split(" × ")[0].strip()
                    element_class = element_name.split(".")[0].replace("Type", "")  # Get the part before the dot
                    attribute = element_name.split(".")[-1]  # Get the part after the dot
                    
                    # Match if the path element matches the element class
                    if path_element == element_class:
                        print(f"    ✓ Match found: {path_element} == {element_class}")
                        # Create path_data entry: "full/path × description"
                        description = element.split(" × ")[1:] if " × " in element else ""
                        path_data.append(f"{path}.{attribute} × {description}")
            
            print(f"Created path_data with {len(path_data)} entries from {len(alphabet_paths)} alphabet paths")

            log = ""

            
            
            for file in os.listdir("variables/sections"):
                section_name = file.split('.')[0]  # Get section name without .txt extension
                
                with open(os.path.join("variables/sections", file), "r") as f:
                    section_data = f.read()
                    section_path_elements = []  # Store path_data entries for this section
                    
                    # Get all lines from this section
                    section_lines = [line.strip() for line in section_data.split("\n") if line.strip()]
                    
                    # Find matching path elements for this section
                    for line in section_lines:
                        # The line IS the path, so find matching path_data entries
                        for path_entry in path_data:
                            path = path_entry.split(" × ")[0]
                            
                            # Check if this path belongs to this section (starts with the section path)
                            if path.startswith(line) or path == line:
                                section_path_elements.append(path_entry)
                    
                    # Remove duplicates while preserving order
                    section_path_elements = list(dict.fromkeys(section_path_elements))
                    
                    print(f"Section: {section_name}")
                    print(f"Path Elements found: {len(section_path_elements)}")
                    if len(section_path_elements) <= 5:
                        print(section_path_elements)
                    else:
                        print(f"Sample path elements: {section_path_elements[:3]}...")
                    
                    log += f"Section: {section_name}\nPath Elements found: {len(section_path_elements)}\n\n"
                    for elem in section_path_elements:
                        log += elem + "\n"
                    log += "\n\n-----\n\n"
                    
                    # Create vector database using path_data entries
                    if section_path_elements:
                        db = Chroma.from_texts(
                            texts=section_path_elements,
                            embedding=ef,
                            collection_name=section_name,
                            persist_directory="expandedRag"
                        )
                        print(f"✓ Created vector database for {section_name} with {len(section_path_elements)} path elements")
                    else:
                        print(f"⚠ No path elements found for section {section_name}")
                    
                    print("\n\n-----\n\n")
                    
            db = Chroma.from_texts(
                texts=path_data,
                embedding=ef,
                collection_name="IPC_ALL",
                persist_directory="expandedRag"
            )
                    
            with open("variables/pdf_log.txt", "w", encoding="utf-8") as f:
                f.write(log)
                        
        except Exception as e:
            print("Error: "+str(e))
                
            
        
if __name__ == "__main__":
    pdf_reader()