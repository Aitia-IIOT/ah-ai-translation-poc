import os
import re
import datetime as _dt
import xml.etree.ElementTree as ET
import pandas as pd
from typing import Dict, List, Optional, Tuple


# Enhanced XSD schema parser with sophisticated type resolution
# Based on AddDefaultValues.py with auto_var2.py dataframe functionality


XSD_NS = "{http://www.w3.org/2001/XMLSchema}"
TN_NS = "http://webstds.ipc.org/2581"


class SimpleTypeInfo:
    def __init__(
        self,
        name: Optional[str],
        base: Optional[str],
        enumerations: Optional[List[str]] = None,
        min_incl: Optional[str] = None,
        max_incl: Optional[str] = None,
        min_excl: Optional[str] = None,
        max_excl: Optional[str] = None,
        pattern: Optional[str] = None,
    ):
        self.name = name
        self.base = base  # QName like 'xsd:string' or a named simpleType
        self.enumerations = enumerations or []
        self.min_incl = min_incl
        self.max_incl = max_incl
        self.min_excl = min_excl
        self.max_excl = max_excl
        self.pattern = pattern


class AttributeInfo:
    def __init__(
        self,
        name: str,
        type_name: Optional[str],
        use: Optional[str],
        default: Optional[str],
        fixed: Optional[str],
        inline_simple_type: Optional[SimpleTypeInfo] = None,
    ):
        self.name = name
        self.type_name = type_name  # QName or named simple type
        self.use = use
        self.default = default
        self.fixed = fixed
        self.inline_simple_type = inline_simple_type


class ComplexTypeInfo:
    def __init__(self, name: str):
        self.name = name
        self.attributes: List[AttributeInfo] = []


def _qname(local: str) -> str:
    return f"{XSD_NS}{local}"


def parse_simple_type(node: ET.Element) -> SimpleTypeInfo:
    name = node.get("name")
    restriction = node.find(_qname("restriction"))
    base = restriction.get("base") if restriction is not None else None
    enums = []
    min_incl = max_incl = min_excl = max_excl = pattern = None
    if restriction is not None:
        for child in restriction:
            tag = child.tag
            if tag == _qname("enumeration"):
                val = child.get("value")
                if val is not None:
                    enums.append(val)
            elif tag == _qname("minInclusive"):
                min_incl = child.get("value")
            elif tag == _qname("maxInclusive"):
                max_incl = child.get("value")
            elif tag == _qname("minExclusive"):
                min_excl = child.get("value")
            elif tag == _qname("maxExclusive"):
                max_excl = child.get("value")
            elif tag == _qname("pattern"):
                pattern = child.get("value")
    return SimpleTypeInfo(name, base, enums, min_incl, max_incl, min_excl, max_excl, pattern)


def parse_attribute(node: ET.Element) -> AttributeInfo:
    name = node.get("name")
    type_name = node.get("type")
    use = node.get("use")
    default = node.get("default")
    fixed = node.get("fixed")
    inline_st: Optional[SimpleTypeInfo] = None
    # Handle inline simpleType
    st = node.find(_qname("simpleType"))
    if st is not None:
        inline_st = parse_simple_type(st)
    return AttributeInfo(name=name, type_name=type_name, use=use, default=default, fixed=fixed, inline_simple_type=inline_st)


def parse_complex_type(node: ET.Element) -> ComplexTypeInfo:
    name = node.get("name")
    cti = ComplexTypeInfo(name)
    # Attributes can be directly under complexType or under attributeGroup, but here we focus on direct attributes
    for attr in node.findall(_qname("attribute")):
        cti.attributes.append(parse_attribute(attr))
    # Note: attributeGroup not handled; extend here if needed
    return cti


def load_schema_info(xsd_path: str) -> Tuple[Dict[str, str], Dict[str, ComplexTypeInfo], Dict[str, SimpleTypeInfo]]:
    tree = ET.parse(xsd_path)
    root = tree.getroot()

    # Gather all simple types by name
    simple_types: Dict[str, SimpleTypeInfo] = {}
    for st in root.findall(_qname("simpleType")):
        sti = parse_simple_type(st)
        if sti.name:
            simple_types[sti.name] = sti

    # Gather all complex types by name
    complex_types: Dict[str, ComplexTypeInfo] = {}
    for ct in root.findall(_qname("complexType")):
        cti = parse_complex_type(ct)
        if cti.name:
            complex_types[cti.name] = cti

    # Map global elements to their declared type (if any)
    element_type_map: Dict[str, str] = {}
    for el in root.findall(_qname("element")):
        el_name = el.get("name")
        el_type = el.get("type")
        if el_name and el_type:
            # Store by local element name; schema uses named complex types like 'ComponentType'
            element_type_map[el_name] = el_type

    return element_type_map, complex_types, simple_types


def _is_numeric_base(base: str) -> bool:
    return base in ("xsd:decimal", "xsd:double", "xsd:float", "xsd:integer", "xsd:int", "xsd:long", "xsd:short", "xsd:byte", "xsd:nonNegativeInteger");


def _type_chain(simple_types: Dict[str, SimpleTypeInfo], type_name: Optional[str]) -> List[SimpleTypeInfo]:
    chain: List[SimpleTypeInfo] = []
    visited = set()
    current = type_name
    while current and current not in visited:
        visited.add(current)
        if current.startswith("xsd:"):
            chain.append(SimpleTypeInfo(name=current, base=current))
            break
        sti = simple_types.get(current)
        if not sti:
            break
        chain.append(sti)
        current = sti.base
    return chain


def _resolve_xsd_base(simple_types: Dict[str, SimpleTypeInfo], type_name: Optional[str]) -> Optional[str]:
    """
    Resolve the ultimate XSD base (e.g., 'xsd:string', 'xsd:integer') for a given type name.
    """
    if not type_name:
        return None
    if type_name.startswith("xsd:"):
        return type_name
    chain = _type_chain(simple_types, type_name)
    for sti in reversed(chain):
        if sti.base and sti.base.startswith("xsd:"):
            return sti.base
    return None


def choose_default_for_attr(attr: AttributeInfo, simple_types: Dict[str, SimpleTypeInfo]) -> str:
    # Fixed takes precedence
    if attr.fixed is not None:
        return attr.fixed
    # Explicit default from XSD
    if attr.default is not None:
        return attr.default

    # Determine effective simple type info (inline or by reference)
    enums: List[str] = []
    pattern = None
    min_incl = None
    xsd_base: Optional[str] = None

    if attr.inline_simple_type is not None:
        sti = attr.inline_simple_type
        enums = sti.enumerations
        pattern = sti.pattern
        min_incl = sti.min_incl
        xsd_base = _resolve_xsd_base(simple_types, sti.base)
    else:
        chain = _type_chain(simple_types, attr.type_name)
        # Collect first enumeration list found up the chain
        for sti in chain:
            if sti.enumerations:
                enums = sti.enumerations
                break
        # Resolve ultimate XSD base (xsd:xxx)
        for sti in reversed(chain):
            if sti.base and sti.base.startswith("xsd:"):
                xsd_base = sti.base
                break
        # Collect pattern/minInclusive (closest-first)
        for sti in chain:
            if sti.pattern and pattern is None:
                pattern = sti.pattern
            if sti.min_incl and min_incl is None:
                min_incl = sti.min_incl

    # Rule: if type is string and has enum, default = first enum value
    if enums and xsd_base == "xsd:string":
        return enums[0]

    # Base-derived defaults
    if xsd_base in ("xsd:boolean",):
        return "false"
    if xsd_base in ("xsd:dateTime",):
        return _dt.datetime.now(_dt.timezone.utc).isoformat()
    if xsd_base in ("xsd:date",):
        return "1970-01-01"
    if xsd_base in ("xsd:anyURI",):
        return "http://example.com"
    if xsd_base in ("xsd:base64Binary",):
        return "SGVsbG8="  # "Hello" in base64
    if xsd_base in ("xsd:hexBinary",):
        return "00"
    if xsd_base in ("xsd:positiveInteger",):
        return "1"
    if xsd_base and _is_numeric_base(xsd_base):
        return min_incl if min_incl is not None else "0"

    # Named types commonly used in this XSD
    if attr.type_name in ("nonNegativeDoubleType",):
        return "0"
    if attr.type_name in ("qualifiedNameType",):
        return "DEFAULT"

    # Pattern known types
    if pattern:
        if pattern == "([^:]+)(:[^:]+)?":
            return "DEFAULT"
        if pattern == "[0-9]+(.[0-9]+)*":
            return "1"

    # Fallback
    return "U"


def auto_var2():
    # Load the XSD file
    xsd_path = 'IPC-2581C.xsd'
    
    if not os.path.isfile(xsd_path):
        print(f"ERROR: XSD not found at {xsd_path}")
        return
    
    print("Parsing XSD with enhanced type resolution...", flush=True)
    element_type_map, complex_types, simple_types = load_schema_info(xsd_path)
    print(f"Loaded: {len(simple_types)} simple types, {len(complex_types)} complex types, {len(element_type_map)} elements")

    # Extract attributes for each complexType and build dataframe-compatible structure
    all_attributes = []
    output_lines = []  # For legacy auto_variables.txt format

    for ct_name, cti in complex_types.items():
        # Process attributes declared for this complex type
        for attr in cti.attributes:
            # Generate sophisticated default value
            default_value = choose_default_for_attr(attr, simple_types)
            
            # DataFrame entry
            all_attributes.append({
                'complex_type': ct_name,
                'attribute_name': attr.name,
                'attribute_type': attr.type_name,
                'use': attr.use or 'optional',
                'default_value': default_value,
                'xsd_default': attr.default,
                'fixed': attr.fixed
            })
            
            # Legacy format entry for auto_variables.txt
            use_suffix = " × req" if attr.use == "required" else ""
            type_info = f" {{ {attr.type_name} }}" if attr.type_name and not attr.type_name.startswith("xsd:") else ""
            
            legacy_line = f"{ct_name}.{attr.name} × {attr.type_name or 'unknown'}{type_info} × {default_value}{use_suffix}"
            output_lines.append(legacy_line)

    # Create DataFrame
    df_attributes = pd.DataFrame(all_attributes)

    # Save to legacy format (maintains compatibility)
    txt_output_file = 'variables/auto_variables.txt'
    os.makedirs(os.path.dirname(txt_output_file), exist_ok=True)
    with open(txt_output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))


if __name__ == "__main__":
    auto_var2()