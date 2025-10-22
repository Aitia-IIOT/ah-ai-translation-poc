import pandas as pd
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
import openai
import json
import re

def parse_element_info(element_text):
    """
    Parse element information from the vector store format.
    Expected formats:
    1. String: "ComplexType.attribute × type × default × requirement × description"
    2. String representation of list: "['type', 'default', 'req', 'description']"
    """
    # Try parsing as × separated string first
    if " × " in element_text:
        parts = element_text.split(" × ")
        if len(parts) >= 2:
            return {
                "full_path": parts[0].strip(),
                "type": parts[1].strip() if len(parts) > 1 else "unknown",
                "default": parts[2].strip() if len(parts) > 2 else "",
                "requirement": parts[3].strip() if len(parts) > 3 else "",
                "description": " × ".join(parts[4:]).strip() if len(parts) > 4 else ""
            }
    
    # Try parsing as list representation (fallback for different vector store format)
    # Format: "path (['type', 'default', 'req', 'description'])"
    if "[" in element_text and "]" in element_text:
        try:
            # Extract path (before the list)
            path_match = element_text.split("([")[0].strip()
            # Extract list content
            list_match = re.search(r'\[(.*?)\]', element_text)
            if list_match:
                list_str = list_match.group(1)
                # Parse the list items
                parts = [item.strip().strip("'\"") for item in list_str.split(",")]
                if len(parts) >= 2:
                    return {
                        "full_path": path_match,
                        "type": parts[0].strip() if len(parts) > 0 else "unknown",
                        "default": parts[1].strip() if len(parts) > 1 else "",
                        "requirement": parts[2].strip() if len(parts) > 2 else "",
                        "description": ", ".join(parts[3:]).strip() if len(parts) > 3 else ""
                    }
        except Exception as e:
            print(f"    Parse error: {e}")
    
    return None

def select_best_element_with_llm(ec_tag, ec_description, retrieved_elements, used_elements):
    """
    Use LLM to select the best matching IPC element with validation.
    Returns tuple: (element_name, confidence_score)
    """
    
    # Parse all retrieved elements
    candidates = []
    for elem in retrieved_elements:
        parsed = parse_element_info(elem.page_content)
        if parsed:
            # Mark if already used
            already_used = parsed["full_path"] in used_elements
            candidates.append({
                "element": parsed["full_path"],
                "type": parsed["type"],
                "description": parsed["description"],
                "raw": elem.page_content,
                "used": already_used
            })
    
    if not candidates:
        return ("-", 0)
    
    # Build candidate list for LLM with usage indicators and exact match highlights
    candidate_lines = []
    ec_tag_normalized = ec_tag.lower().replace(" ", "").replace("-", "")
    
    for i, c in enumerate(candidates):
        # Check if attribute name matches EC tag
        attr_name = c['element'].split('.')[-1].lower() if '.' in c['element'] else ""
        is_exact_match = ec_tag_normalized in attr_name or attr_name in ec_tag_normalized
        
        status_flags = []
        if is_exact_match:
            status_flags.append("✨ EXACT NAME MATCH")
        if c['used']:
            status_flags.append("⚠️ ALREADY USED")
        
        status_str = f"  {' | '.join(status_flags)}" if status_flags else ""
        
        candidate_lines.append(
            f"{i+1}. {c['element']} (Type: {c['type']}){status_str}\n   Description: {c['description'][:200]}"
        )
    
    candidate_text = "\n".join(candidate_lines)
    
    # Show already mapped elements for context
    used_context = ""
    if used_elements:
        recent_used = list(used_elements[-10:]) if len(used_elements) > 10 else list(used_elements)
        used_context = f"\n\nAlready mapped elements (AVOID REUSE):\n" + "\n".join([f"- {elem}" for elem in recent_used])
    
    # LLM selection prompt
    selection_prompt = f"""You are an expert at mapping Electronic Component (EC) metadata to IPC-2581 XML schema elements.

EC Tag: {ec_tag}
EC Description: {ec_description}

Available IPC-2581 candidates:
{candidate_text}{used_context}

Task: Select the BEST and MOST SPECIFIC matching IPC element for this EC tag.

CRITICAL MAPPING RULES:
1. **EXACT ATTRIBUTE NAME MATCH = HIGHEST PRIORITY**: If an element's attribute name matches the EC tag, strongly prefer it
   - EC "Weight" → Component.weight, Package.weight, etc. (EXACT MATCH = 95-100% confidence)
   - EC "Manufacturer" → *.manufacturer, *.vendor fields
   - EC "Package" → *.package, Package.name fields
   - EC "Description" → *.description fields

2. **AVOID DUPLICATES**: Do NOT select elements marked "⚠️ ALREADY USED" unless absolutely no other option exists

3. **SEMANTIC SPECIFICITY**: Choose elements whose PURPOSE matches the EC tag, not just "can hold a string"
   - "Description" → description/comment fields
   - "Part Number" → part/mpn/designNumber fields  
   - "Manufacturer" → manufacturer/vendor/enterprise fields
   - "Package" → package-related fields
   - "Weight" → weight/mass fields
   - "Specification" → specification/standard fields

4. **TYPE APPROPRIATENESS**: Match data types logically
   - Identifiers → string/qualifiedName types
   - Numbers → double/integer types
   - Yes/No → boolean types

5. **CONTEXT HIERARCHY**: Prefer elements in appropriate sections
   - Component data → Bom/Avl/Component elements
   - Design data → Ecad/CadData elements
   - Metadata → Content/Header elements

SCORING GUIDELINES:
- Exact attribute name match (✨) + unused = 95-100% confidence (BEST!)
- Exact match but USED = 70-80% confidence (still good but penalized)
- Strong semantic + type match + unused = 85-95% confidence
- Good semantic match but used = 50-60% confidence (penalized)
- Generic "comment" field for specific data = 40-50% confidence (weak)
- Wrong context/purpose = 0-30% confidence (reject)

Respond in JSON format:
{{
    "selected_number": <1-{len(candidates)} or 0 for no match>,
    "confidence": <0-100>,
    "reasoning": "<explain semantic match and why this element is best>"
}}

Only return selected_number: 0 if NO candidate has semantic alignment with the EC tag."""

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a precise technical mapping assistant."},
                {"role": "user", "content": selection_prompt}
            ],
            temperature=0.1
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Extract JSON from response
        json_match = re.search(r'\{[^}]+\}', result_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            selected_num = result.get("selected_number", 0)
            confidence = result.get("confidence", 0)
            reasoning = result.get("reasoning", "")
            
            print(f"  LLM Selection: #{selected_num}, Confidence: {confidence}%")
            print(f"  Reasoning: {reasoning}")
            
            # Validate selection
            if selected_num > 0 and selected_num <= len(candidates) and confidence >= 40:
                selected = candidates[selected_num - 1]
                return (selected["element"], confidence)
        
    except Exception as e:
        print(f"  LLM selection error: {e}")
    
    return ("-", 0)

def translation():
    element_list = []

    with open("IPC-2581C_elements.json", encoding="utf-8") as f:
        data = json.load(f)

    name_list = [element["name"].lower() for element in data["Elements"]]

    with open("variables/rich_auto_variables.txt", encoding="utf-8") as f:
        element_with_names = f.read().splitlines()

    #Insert key for OpenAI

    embedding_function = OpenAIEmbeddings(api_key="xyz")

    #Insert Azure OpenAI parameters

    openai.api_type = "xyz"
    openai.azure_endpoint = "xyz"
    openai.api_version = "xyz"
    openai.api_key = "xyz"


    tags = pd.read_csv('TagsMeaning.csv', sep=';')
    output ="EC_tag;IPC_element\n"
    aianswers = ""
    used_elements = []

    for line in tags.values:
        
        # Format the prompt properly as a string
        user_prompt = f'''
            Available categories:
            1. Avl – The AVL (Approved Vendor List) contains manufacturer and supplier approval data for parts and materials used in production. Each entry typically associates a part number with one or more authorized vendors, including manufacturer names, part numbers, status (e.g., approved, qualified, obsolete), and sourcing restrictions.
            2. Bom – The BOM (Bill of Materials) defines the hierarchical structure of a product — listing all assemblies, subassemblies, and components required to manufacture or build it. Each item may include quantity, reference designators, sourcing info, and version or revision details.
            3. Content – Content encompasses all descriptive, textual, and document-based information related to parts, assemblies, and processes. It includes metadata (e.g., part descriptions, categories, lifecycle states) and associated digital assets such as datasheets, drawings, and specifications.
            4. LogisticHeader – The LogisticHeader contains high-level logistics and transaction metadata used to manage the physical or digital flow of goods and data. It typically includes shipment identifiers, routing IDs, source and destination locations, carrier information, shipment dates, and package counts.
            5. HistoryRecord – The HistoryRecord logs changes, transactions, or routing events applied to data objects such as BOMs, AVL entries, or ECAD integrations. Each record typically captures timestamp, user or system identifier, action type, and data deltas.
            6. Ecad – ECAD data includes electronic design information from PCB layout and schematic tools such as Altium, Cadence, or Mentor. It may contain component symbols, footprints, netlists, reference designators, and layout constraints.

            Given the task below, identify which category (or categories) should be accessed or modified.

            Task:
            {line[1].lower()}

            Respond should contain only the category name that is relevant.
            You must choose one and only one category!
            The response must be one of the six categories above, and it is case-sensitive.
            '''
        
        
        
        print(line[0])
        prompt_list = [{"role": "system", "content": "You are a router agent responsible for selecting the correct data category based on the task."}, 
                    {"role": "user", "content": user_prompt}]
            
        response = openai.chat.completions.create(model="gpt-4o", messages=prompt_list) 
        layer = response.choices[0].message.content.strip()
        print(f"Layer: {layer}")

        if layer in ["Avl", "Bom", "Content", "LogisticHeader", "HistoryRecord", "Ecad"]:
            element_name = None
            
            vectorestore_cat = Chroma(persist_directory="expandedRag", collection_name=f"{layer}")
            vectorestore_cat._embedding_function = embedding_function
            
            vectorestore_all = Chroma(persist_directory="expandedRag", collection_name="IPC_ALL")
            vectorestore_all._embedding_function = embedding_function

            # HYBRID SEARCH: Combine semantic + attribute name matching
            # 1. Semantic search for description match
            retrived_semantic_cat = vectorestore_cat.similarity_search(query=line[1], k=3)

            # 2. Keyword search for attribute name match (e.g., "weight" → Component.weight)
            ec_tag_lower = line[0].lower().replace(" ", "").replace("-", "")
            retrived_keyword = vectorestore_all.similarity_search(query=ec_tag_lower, k=3)
            
            # 3. Semantic search across ALL categories for broader matches
            retrived_semantic_all = vectorestore_all.similarity_search(query=line[1], k=3)

            # Combine and deduplicate by page_content
            seen_content = set()
            retrived = []
            
            # Prioritize keyword matches (exact attribute names)
            for elem in retrived_keyword:
                if elem.page_content not in seen_content:
                    retrived.append(elem)
                    seen_content.add(elem.page_content)
            
            # Add semantic matches
            for elem in retrived_semantic_cat:
                if elem.page_content not in seen_content:
                    retrived.append(elem)
                    seen_content.add(elem.page_content)
                
            # Add semantic matches
            for elem in retrived_semantic_all:
                if elem.page_content not in seen_content:
                    retrived.append(elem)
                    seen_content.add(elem.page_content)
            
            print(f"\nRetrieved {len(retrived)} candidates (hybrid: keyword + semantic):")
            ec_tag_normalized = line[0].lower().replace(" ", "").replace("-", "")
            
            for i, element in enumerate(retrived):
                # Debug: show raw format
                if i == 0:
                    print(f"  [DEBUG] Raw format: {element.page_content[:150]}...")
                    print(f"  [DEBUG] Searching for EC tag: '{line[0]}' (normalized: '{ec_tag_normalized}')")
                
                parsed = parse_element_info(element.page_content)
                if parsed:
                    # Check for exact attribute name match
                    attr_name = parsed['full_path'].split('.')[-1].lower() if '.' in parsed['full_path'] else ""
                    is_exact = ec_tag_normalized in attr_name or attr_name in ec_tag_normalized
                    match_indicator = " ✨ EXACT NAME MATCH" if is_exact else ""
                    
                    print(f"  {i+1}. {parsed['full_path']} (Type: {parsed['type']}){match_indicator}")
                    if i < 3:  # Show description for first 3
                        print(f"      Desc: {parsed['description'][:100]}...")
                else:
                    print(f"  {i+1}. [PARSE FAILED] {element.page_content[:100]}...")
            
            # Use LLM to select best element with validation
            element_name, confidence = select_best_element_with_llm(
                ec_tag=line[0],
                ec_description=line[1],
                retrieved_elements=retrived,
                used_elements=used_elements
            )
            
            print(f"Final choice: {element_name} (confidence: {confidence}%)")
            
            # Add to output
            output += f"{line[0]};{element_name}\n"
            
            # Track ALL successful mappings to avoid reuse (not just high-confidence)
            if element_name != "-":
                used_elements.append(element_name)
            
            # Store the result for analysis
            aianswers += f"Query: {line[1]} -> Layer: {layer} -> Element: {element_name} (confidence: {confidence}%)\n"
        else:
            print(f"Invalid layer: {layer}")
            output += f"{line[0]};INVALID_LAYER\n"
            aianswers += f"Query: {line[1]} -> Layer: {layer} -> Element: INVALID_LAYER\n"
            
        print ("\n\n-----\n\n")
    
    print ("\n\n-----\n\n")

    with open(f"mapping_table/EC_IPC.csv", "w", encoding="utf-8") as f:
        f.write(output)

if __name__ == "__main__":
    translation()
    
