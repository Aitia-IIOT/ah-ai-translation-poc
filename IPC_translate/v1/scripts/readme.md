# 💱 AI Translation by AITIA.AI

This project is a work-in-progress for a fully automated script.

### Current Workflow
Until the automation is complete, the scripts should be run in the following order:

1. `auto_tree.py`
2. `auto_var2.py`
3. `pdf_reader.py`
4. `translation2_0.py` (runs `duplicate_output_detection.py`)
5. `tag_swap2.py` (uses `find_element_in_tree.py`)

---

### 🛠️ Fixes and Updates

#### ⚙️ <span style="color:rgb(190, 150, 150)"> v1.0.1 </span>:
- **`find_element_in_tree.py`:** Replaced the handmade `complex_class_tree` with `auto_tree`.
- **`tag_swap2.py`:** Integrated the required tags into the output.
- **`../test`:** Input chunked by row and a set of outputs for it.

#### ⚙️ <span style="color:rgb(100, 200, 50)"> v1.1 (currently live) </span>:
- **`auto_tree.py`:** Now on it's using DFS instead of BFS to match the order of elements described in the `.xsd` file. Also it creates a `req_classes.txt`, that contains all the tags that it needs to open if the parent is open.
- **`tag_swap2.py`:** As per above, it now implements all the required class (only which needed to be open) and it uses the new 'custom order' instead of alphabetical order.

---

## Documentation

### I. Understanding the required technologies

#### Retrieval Augmented Generation (RAG)
RAG is a hybrid and innovative approach that enables the combination of the generative capabilities of large language models with information retrieval from external knowledge bases (such as databases consisting of documents, web pages, etc.). Its structure typically requires a **vector database** and a **retriever** object—the latter is responsible for returning the relevant information.

First, the relevant information that will form the knowledge base needs to be collected. Then, this data must be broken down into smaller chunks and vectorized using an embedding model. This means that from now on, our data will be represented numerically in n-dimensional space. Once this is done, the resulting vectors are stored in a vector database. Searches can then be performed within this database using a retriever object, which returns the closest vectors based on distance—now in textual form.

Finally, this retrieved information can be injected into the prompt for the large language model, which can then utilize it. This allows the model to access external information, thereby reducing the occurrence of **hallucinations**.

#### Vector database

A vector database is a specialized storage and search system capable of storing texts in a multidimensional numerical format. Thanks to this, it enables fast **approximate nearest neighbor search (ANNS)**.

Its operation is based on numerical representation—for example, if only binary values are stored, the search could be performed using **Hamming distance**, meaning it would return the row with the fewest differing columns. Most implementations on the market—including the **Chroma** vector database that I use—primarily use **cosine-based distance metrics** by default.

#### Hallucination 

**Hallucination** is the phenomenon where a large language model returns an incorrect or inappropriate response to the user. This typically occurs when the model lacks sufficient knowledge in the given subject area. In this case, the standard used for testing is a paid one, so it is almost certain that it was not included in the training data. As a result, the model would likely not provide a useful answer.

---

### II. System

#### Architecture

<img src="system_arch.svg">

The figure illustrates the structure of the system I developed, where each module is a separate Python program, each performing a different task. I prefer the modular breakdown because it aligns with the microservices-based architecture I studied during my specialization. This approach also makes it possible to deploy the system as a cloud-based web service in the future.

The system can be divided into four main parts:

1) Preprocessing section <span style="color:rgb(131, 161, 231)"> (Lavender)</span>,

2) Translation module <span style="color:rgb(225, 213, 231)"> (Lilac)</span>,

3) Output module <span style="color:rgb(255, 230, 204)">(Peach)</span>, and

4) Support modules that assist the operation of the others <span style="color:rgb(176, 219, 248)"> (Cornflower Blue)</span>.

The preprocessing section is responsible for handling complex documents that require detailed parsing. This helps improve the accuracy and consistency of the translation module and ensures that the output file adheres to the tree hierarchy defined in the .xsd file.

The following chapters briefly describe the functionality of the modules shown in the figure.

#### Brief Description of System Components

##### **Automatic tree generator**

This module performs three tasks, all within a single iteration over the input `.xsd` file.

1. **Tree Construction**
   During the first task, the program constructs a tree by identifying child elements for each parent element and storing them in the format `Parent.Child`. At the end of the iteration, it scans through the collected pairs to find the element that appears only as a parent—this is identified as the **root element**. From this root, a **breadth-first traversal** is performed to build the complete tree structure. The resulting tree is saved in `tree.json` using the following format:

   ```json
   {"id": 1, "name": "IPC-2581", "parent": null}
   ```

2. **Required Children Extraction**
   In the second task, during the same iteration, the module collects those `Parent.Child` pairs where the child element is **mandatory** (i.e., has a minimum occurrence of at least one) when the parent element is opened.

3. **Order Resolution**
   In the third task, a **depth-first traversal** is performed on the constructed tree to determine the exact **element order** expected by the `.xsd` file. This ensures that the final output preserves the schema-defined structure and sequence.

##### **Automatic Variable Gatherer**

This module implements a solution similar to the previous one. It reads the input file line by line, extracting the declared variables for each element. If a field is marked as mandatory, this information is included in the output file.
The generated output contains, for each variable, its name, type, and constraints—such as the allowed pattern for strings or possible values in the case of enums—thus simplifying the translation process.

##### **Mapping Table Creator**
This is the part of the system where the **artificial intelligence** component plays a central role. The vector database generated by the previously mentioned module becomes particularly useful here, as a simple prompt would not be sufficient. This is because the tested standard is **not included in the training data** of the large language model we are using. Without proper context, the model would return incorrect or hallucinated responses.

This is where the **RAG (Retrieval-Augmented Generation)** architecture comes into play. First, a **Retriever** object must be declared. This component vectorizes the input—specifically, the description of the input variable—and returns the **top-k most semantically similar** entries from the vector database (in this case, the top 2).

Next, a **prompt template** is used, which is a pre-written prompt containing placeholders. The retrieved entries are then **injected into these placeholders**, providing the model with the **necessary context** to generate a reliable response, significantly reducing the chances of hallucination.

Finally, this enriched prompt is sent to the model (in this case, **Azure GPT-4o**), which determines whether either of the two retrieved output variables can **natively store** the value of the input standard variable—that is, whether they satisfy the type and constraints (e.g., enum values, string patterns, etc.).

* If **both** are capable, a **second call** is made to decide which one is more appropriate.
* If **neither** is suitable, we interpret this as the output standard being unable to represent the input variable, and no mapping is assigned.

In the end, the resulting variable pairs are written to a `.csv` file.


##### **Duplication Checker**
This is one of the support modules and also utilizes artificial intelligence. Its responsibility is to resolve any **duplicate entries** that may appear in the translation table—specifically, when **two elements are mapped to the same output variable**. The resolution process follows these steps:

1. **Select the Best Match**
   Among the duplicated variables, the module determines which one is the **best fit** for the shared output variable. This one retains the mapping, while the others are **unassigned** from that variable.

2. **Prevent Future Duplicates**
   To avoid repeated duplications, the module **removes the used output variable** from the vector database. This ensures it will not be selected again for another input variable.

3. **Reassignment Attempt**
   For each unassigned variable, the module **repeats the prompt generation and evaluation process** used in the previous module, attempting to assign a new, suitable output variable. In some cases, however, a match may not be found.

This process continues **iteratively** until all duplications are resolved.

##### **Element searcher in tree**

This is the second support module in the system, designed to assist the output module by precisely locating elements listed in the translation table. It works by searching for the given input element in the tree structure and then tracing the path back to the root node, providing a clear view of the element’s exact location.

This is made possible by the way the tree is stored: since each element includes a "parent" field pointing to the unique identifier of its parent, the module can iteratively traverse upward in the tree until it reaches the root node—where the parent value is "null".

It’s possible that an element may appear multiple times in the tree. In such cases, the current version of the module notifies the user, presents all possible matches, and prompts the user to choose the correct one.

##### **XML Embedding Modul**
This is the final output module—and arguably the most complex—since it integrates all the threads from the previous modules. Accordingly, the module’s functionality is best described by following the actual sequence of operations, which roughly mirrors its real execution flow.

---

1. **Loading Input Data**
   The module begins by reading the previously generated **translation table**, along with all required classes. Using the **Element Finder in the Tree** module, it determines the exact **locations of the translated elements** within the output tree structure.

2. **Ordering Elements**
   Once all positions are known, the elements are **sorted** according to the “alphabet” created by the **Automatic Tree Generator**. This ordering is crucial—it dictates which elements must be opened or closed during file generation and ensures correct nesting and structure.

3. **Reading the Input Standard**
   The program then reads the input file based on the source standard. This file contains **169 distinct sections**, each separated by `<row>` elements. Each `<row>` is handled **independently**, generating its own tree structure.

   The content between `<row>` tags is stored and processed once the closing tag is reached. For each section, the program matches the used variables to their equivalents in the output standard and begins building the corresponding **output tree**, based on the previously determined, ordered **path sequences**.

4. **Element Nesting Logic**
   During output generation, the module takes into account whether an opened element has any **required nested elements or variables**, inserting them where appropriate.

   * **Opening Elements**: The program compares the current path with the previous one and opens only the elements that are **not already open**, maintaining structural correctness and nesting.
   * **Closing Elements**: The reverse principle is applied—any unmatched, no-longer-needed elements are closed. Failing to do so can cause serious issues: **incorrect output structure**, **excessive file size**, and **increased runtime** (sadly confirmed from experience).

---

**Example:**

```
IPC-2581/Content/DictionaryFillDesc/EntryFillDesc  
IPC-2581/Content/DictionaryStandard/EntryStandard
```

After outputting the first line, the following elements are open:
`IPC-2581`, `Content`, `DictionaryFillDesc`, `EntryFillDesc`.

For the second line, we see that only the first **two elements match**.
So, `EntryFillDesc` and `DictionaryFillDesc` must be closed, and then `DictionaryStandard` and `EntryStandard` are opened.

This careful open-close logic ensures that the generated **XML output is well-formed, valid, and optimized**.

---

### III. Results
As you can see in the `..\test` folder, the order of elements / variables following the rules of the `.xsd` file, thus it is correct. The only concern now that remains if the following: finding a way to check if the selected variable is the best that we could choose, a.k.a. somehow measure the precision.
The closest thing that we can measure now is the consistency of a serie of mapping table, like in 10 runs how the output variables change. Currently this value after **10 runs** is **around 85% (0.85)** with the **median of 0.9** in range [0,1].

---

### IV. Future work

#### **Repeatedly Represented Elements in the Tree**

The current standard contains **six top-level elements**, which can be assumed to have entirely distinct purposes and descriptions. Based on this, I believe the system's **efficiency and consistency** could be improved by transforming the current **single-layer vector database** into a **multi-level (hierarchical) vector database**.

With such a system, there would be no need to search through **all available variables**—instead, the search would be limited to a **specific category**, determined by analyzing the **input variable's description**. This category would correspond to one of the top-level branches.

Additionally, by knowing **which branch** an element belongs to, the system would be able to **more precisely and consistently locate its correct position** in the output structure. In most cases, this would allow us to **uniquely identify** the proper location for a given element, thereby reducing ambiguity and improving structural integrity.

#### **Prompt Tuning**
Naturally, this is always a recommended area for improvement, as **prompts can almost always be slightly optimized** to enhance the **consistency and accuracy** of the model’s responses. Even small refinements in phrasing, structure, or context injection can significantly reduce hallucinations and improve semantic alignment between input and output variables.

#### Involving Additional Standard-Issuing Organizations**
To further **refine the model** and identify **edge cases or uncovered issues**, it would be essential to **collaborate with more companies** that work with **XML-based standards**. Their participation could bring new types of data structures, usage scenarios, and constraints into the system, thereby increasing its robustness and generalizability across different industrial and regulatory domains.

#### Automatic value pairing to required variables
It's nice that the system inserts into the tags, but they are just "", which could cause problem e.g. in enums. There is no specified construction here, but it is a required step.
