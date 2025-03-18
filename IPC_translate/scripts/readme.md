# 💱 AI Translation

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

#### ⚙️ v1.0.1:
- **`find_element_in_tree.py`:** Replaced the handmade `complex_class_tree` with `auto_tree`.
- **`tag_swap2.py`:** Integrated the required tags into the output.
- **`../test`:** Input chunked by row and a set of outputs for it.