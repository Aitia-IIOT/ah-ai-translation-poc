import argparse
import csv
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


IPC2581_NS = "http://webstds.ipc.org/2581"
XSD_NS = "http://www.w3.org/2001/XMLSchema"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
DEFAULT_MAPPING_CSV = "EC_IPC.csv"
DEFAULT_ORIGINAL_XML = "Start.xml"


@dataclass(frozen=True)
class MappingEntry:
	source_field_raw: str
	source_field_norm: str
	target: str


def _sanitize_tag_name(name: str) -> str:
	"""Convert non-XML-ish tag names (e.g. containing spaces) into a safe tag name.

	Note: This is used for parsing the input pseudo-XML. The raw field name is
	preserved for output attributes where required (e.g. Textual@name).
	"""
	name = name.strip()
	name = re.sub(r"\s+", "_", name)
	name = re.sub(r"[^A-Za-z0-9_:\-\.]+", "_", name)
	name = re.sub(r"_+", "_", name)
	return name


def _normalize_pseudo_xml_tags(xml_text: str) -> str:
	"""Normalize tags so that space-containing tag names become parseable XML.

	Example: <EPPL Family> -> <EPPL_Family>
	         </EPPL Family> -> </EPPL_Family>

	This function also preserves self-closing tags like <ASA />.
	"""

	def repl(match: re.Match[str]) -> str:
		inner = (match.group(1) or "").strip()
		if not inner:
			return match.group(0)

		# Leave declarations/comments/doctype untouched
		if inner.startswith("?") or inner.startswith("!"):
			return match.group(0)

		is_closing = inner.startswith("/")
		if is_closing:
			inner = inner[1:].strip()

		# Detect self-closing tags: either endswith '/' or has trailing '/' token.
		is_self_closing = False
		if inner.endswith("/"):
			is_self_closing = True
			inner = inner[:-1].strip()
		else:
			tokens = inner.split()
			if tokens and tokens[-1] == "/":
				is_self_closing = True
				inner = " ".join(tokens[:-1]).strip()

		# In our inputs, tags with spaces do not have attributes.
		sanitized = _sanitize_tag_name(inner)
		suffix = " /" if is_self_closing else ""
		prefix = "/" if is_closing else ""
		return f"<{prefix}{sanitized}{suffix}>"

	pattern = re.compile(r"<([^<>]*?)>")
	return pattern.sub(repl, xml_text)


def _read_mapping_csv(mapping_path: Path) -> List[MappingEntry]:
	with mapping_path.open("r", encoding="utf-8-sig", newline="") as f:
		reader = csv.reader(f, delimiter=";")
		rows = list(reader)

	if not rows:
		raise ValueError("MappingTable is empty")

	mappings: List[MappingEntry] = []
	for row in rows[1:]:
		if len(row) < 2:
			continue
		source_raw = (row[0] or "").strip()
		target = (row[1] or "").strip()
		if not source_raw:
			continue
		if not target or target.lower() == "not included":
			continue
		mappings.append(
			MappingEntry(
				source_field_raw=source_raw,
				source_field_norm=_sanitize_tag_name(source_raw),
				target=target,
			)
		)
	return mappings


def _parse_input_values(input_xml_path: Path) -> Dict[str, str]:
	text = input_xml_path.read_text(encoding="utf-8-sig")
	normalized = _normalize_pseudo_xml_tags(text)
	try:
		root = ET.fromstring(normalized)
	except ET.ParseError as e:
		raise ValueError(
			f"Input XML could not be parsed even after tag normalization: {e}"
		) from e

	values: Dict[str, str] = {}
	for elem in root.iter():
		if elem is root:
			continue
		if elem.text is None:
			continue
		value = elem.text.strip()
		if value == "":
			continue
		# Only store first occurrence (stable + predictable)
		values.setdefault(elem.tag, value)
	return values


def _indent(elem: ET.Element, level: int = 0) -> None:
	i = "\n" + level * "  "
	if len(elem):
		if not elem.text or not elem.text.strip():
			elem.text = i + "  "
		for child in elem:
			_indent(child, level + 1)
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
	else:
		if level and (not elem.tail or not elem.tail.strip()):
			elem.tail = i


def _ns(tag: str, namespace: str) -> str:
	return f"{{{namespace}}}{tag}"


def _find_or_create_child(parent: ET.Element, child_tag: str) -> ET.Element:
	existing = parent.find(child_tag)
	if existing is not None:
		return existing
	child = ET.SubElement(parent, child_tag)
	return child


def _parse_target(target: str) -> Tuple[str, Optional[str]]:
	"""Split a target segment like 'Textual.value' into ('Textual', 'value')."""
	if "." not in target:
		return target, None
	left, right = target.split(".", 1)
	return left, right


def _build_bom_item(
	input_values: Dict[str, str],
	mappings: Iterable[MappingEntry],
	namespace: str,
) -> ET.Element:
	bom_item = ET.Element(_ns("BomItem", namespace))

	prefix = "IPC-2581/Bom/BomItem"
	for entry in mappings:
		value = input_values.get(entry.source_field_norm)
		if not value:
			continue

		target = entry.target
		if not target.startswith(prefix):
			continue

		remainder = target[len(prefix) :]
		if remainder.startswith("."):
			attr_name = remainder[1:]
			if attr_name:
				bom_item.set(attr_name, value)
			continue

		if not remainder.startswith("/"):
			continue
		rel_path = remainder[1:]
		if not rel_path:
			continue

		parts = [p for p in rel_path.split("/") if p]
		current = bom_item

		# Special case flag for Textual.value mapping
		is_textual_value = rel_path.endswith("Characteristics/Textual.value")

		for idx, part in enumerate(parts):
			elem_name, attr_name = _parse_target(part)
			is_last = idx == len(parts) - 1

			elem_tag = _ns(elem_name, namespace)

			if is_last and is_textual_value and elem_name == "Textual" and attr_name == "value":
				# Always create a new Textual entry for each mapping row
				textual = ET.SubElement(current, elem_tag)
				textual.set("name", entry.source_field_raw)
				textual.set("value", value)
				break

			child = _find_or_create_child(current, elem_tag)
			if elem_name == "Characteristics" and "category" not in child.attrib:
				child.set("category", "ELECTRICAL")

			if is_last and attr_name:
				child.set(attr_name, value)
			current = child

	# Defaults required by spec
	internal_part_number = (bom_item.get("internalPartNumber") or "").strip()
	if internal_part_number and not (bom_item.get("OEMDesignNumberRef") or "").strip():
		bom_item.set("OEMDesignNumberRef", internal_part_number)
	if not (bom_item.get("category") or "").strip():
		bom_item.set("category", "ELECTRICAL")
	if not (bom_item.get("quantity") or "").strip():
		bom_item.set("quantity", "1")

	return bom_item


def _append_bom_item(original_xml_path: Path, bom_item: ET.Element) -> ET.ElementTree:
	tree = ET.parse(original_xml_path)
	root = tree.getroot()

	# Determine namespace from root
	namespace = ""
	if root.tag.startswith("{") and "}" in root.tag:
		namespace = root.tag.split("}", 1)[0][1:]

	if not namespace:
		namespace = IPC2581_NS

	bom = root.find(f".//{_ns('Bom', namespace)}")
	if bom is None:
		raise ValueError("Original.xml does not contain a <Bom> element")

	_ensure_refdes_for_all_bom_items(bom=bom, namespace=namespace)
	_ensure_refdes_for_one_bom_item(bom=bom, bom_item=bom_item, namespace=namespace)

	new_refdes = bom_item.find(_ns("RefDes", namespace))
	package_name = None
	refdes_name = None
	if new_refdes is not None:
		refdes_name = (new_refdes.get("name") or "").strip() or None
		package_name = (new_refdes.get("packageRef") or "").strip() or None
	if package_name is None:
		package_name = (bom_item.get("internalPartNumber") or "").strip() or None
	if package_name:
		_ensure_package_for_steps(root=root, namespace=namespace, package_name=package_name)
	if refdes_name and package_name:
		_ensure_component_for_steps(
			root=root,
			namespace=namespace,
			refdes_name=refdes_name,
			package_name=package_name,
		)

	bom.append(bom_item)
	return tree


def _ensure_package_for_steps(root: ET.Element, namespace: str, package_name: str) -> None:
	"""Ensure Ecad/CadData/Step contains a Package for the given name."""
	step_tag = _ns("Step", namespace)
	package_tag = _ns("Package", namespace)
	ecad_tag = _ns("Ecad", namespace)
	cad_data_tag = _ns("CadData", namespace)

	steps: List[ET.Element] = []
	for ecad in root.findall(f".//{ecad_tag}"):
		cad_data = ecad.find(cad_data_tag)
		if cad_data is None:
			continue
		steps.extend(cad_data.findall(step_tag))

	if not steps:
		raise ValueError("Original.xml does not contain Ecad/CadData/Step; cannot add Package")

	for step in steps:
		existing = None
		for pkg in step.findall(package_tag):
			if (pkg.get("name") or "").strip() == package_name:
				existing = pkg
				break

		if existing is None:
			existing = ET.Element(package_tag)
			step.append(existing)

		existing.set("name", package_name)
		existing.set("type", "OTHER")
		existing.set("pinOneOrientation", "LOWER_LEFT")
		existing.set("height", "0.1")


def _ensure_component_for_steps(
	root: ET.Element,
	namespace: str,
	refdes_name: str,
	package_name: str,
) -> None:
	"""Ensure Ecad/CadData/Step contains a Component for the given refdes."""
	step_tag = _ns("Step", namespace)
	component_tag = _ns("Component", namespace)
	ecad_tag = _ns("Ecad", namespace)
	cad_data_tag = _ns("CadData", namespace)

	steps: List[ET.Element] = []
	for ecad in root.findall(f".//{ecad_tag}"):
		cad_data = ecad.find(cad_data_tag)
		if cad_data is None:
			continue
		steps.extend(cad_data.findall(step_tag))

	if not steps:
		raise ValueError("Original.xml does not contain Ecad/CadData/Step; cannot add Component")

	for step in steps:
		existing = None
		for comp in step.findall(component_tag):
			if (comp.get("refDes") or "").strip() == refdes_name:
				existing = comp
				break

		if existing is None:
			existing = ET.Element(component_tag)
			step.append(existing)

		existing.set("refDes", refdes_name)
		existing.set("packageRef", package_name)
		existing.set("part", package_name)
		existing.set("layerRef", "Top Layer")
		# Requirement says mountType (typo preserved as requested)
		existing.set("mountType", "OTHER")
		existing.set("weight", "0")
		existing.set("height", "0.1")
		existing.set("standoff", "0")


def _iter_bom_items(bom: ET.Element, namespace: str) -> Iterable[ET.Element]:
	return bom.findall(_ns("BomItem", namespace))


def _parse_refdes_number(name: str) -> Optional[int]:
	name = (name or "").strip()
	m = re.fullmatch(r"C(\d+)", name)
	if not m:
		return None
	try:
		return int(m.group(1))
	except ValueError:
		return None


def _get_next_refdes_name(bom: ET.Element, namespace: str) -> str:
	max_n = 0
	for item in _iter_bom_items(bom, namespace):
		for refdes in item.findall(_ns("RefDes", namespace)):
			n = _parse_refdes_number(refdes.get("name", ""))
			if n is not None and n > max_n:
				max_n = n
	return f"C{max_n + 1}"


def _insert_element_before_first(parent: ET.Element, new_elem: ET.Element, before_tag: str) -> None:
	children = list(parent)
	for idx, child in enumerate(children):
		if child.tag == before_tag:
			parent.insert(idx, new_elem)
			return
	parent.append(new_elem)


def _normalize_refdes_position(bom_item: ET.Element, namespace: str) -> None:
	"""Ensure all RefDes children appear before the first Characteristics child."""
	refdes_tag = _ns("RefDes", namespace)
	characteristics_tag = _ns("Characteristics", namespace)

	refdes_children = [c for c in list(bom_item) if c.tag == refdes_tag]
	if not refdes_children:
		return

	# If there is no Characteristics, order doesn't matter.
	if bom_item.find(characteristics_tag) is None:
		return

	# Remove and re-insert before Characteristics, preserving original RefDes order.
	for child in refdes_children:
		bom_item.remove(child)
	for child in refdes_children:
		_insert_element_before_first(bom_item, child, characteristics_tag)


def _ensure_refdes_for_one_bom_item(bom: ET.Element, bom_item: ET.Element, namespace: str) -> None:
	existing = bom_item.find(_ns("RefDes", namespace))
	if existing is not None:
		_normalize_refdes_position(bom_item, namespace)
		return

	ref_name = _get_next_refdes_name(bom, namespace)
	internal_part_number = bom_item.get("internalPartNumber", "")

	refdes = ET.Element(_ns("RefDes", namespace))
	refdes.set("name", ref_name)
	refdes.set("packageRef", internal_part_number)
	refdes.set("layerRef", "Top Layer")

	_insert_element_before_first(bom_item, refdes, _ns("Characteristics", namespace))


def _ensure_refdes_for_all_bom_items(bom: ET.Element, namespace: str) -> None:
	# If any existing BomItem is missing RefDes, add one with next available C<number>.
	# Uses a running max to avoid O(n^2) scans.
	max_n = 0
	bom_items = list(_iter_bom_items(bom, namespace))
	for item in bom_items:
		for refdes in item.findall(_ns("RefDes", namespace)):
			n = _parse_refdes_number(refdes.get("name", ""))
			if n is not None and n > max_n:
				max_n = n

	for item in bom_items:
		if item.find(_ns("RefDes", namespace)) is not None:
			_normalize_refdes_position(item, namespace)
			continue
		max_n += 1
		internal_part_number = item.get("internalPartNumber", "")
		refdes = ET.Element(_ns("RefDes", namespace))
		refdes.set("name", f"C{max_n}")
		refdes.set("packageRef", internal_part_number)
		refdes.set("layerRef", "Top Layer")

		_insert_element_before_first(item, refdes, _ns("Characteristics", namespace))


def _resolve_script_sidecar(filename: str) -> Path:
	return Path(__file__).resolve().with_name(filename)


def _resolve_script_child(dirname: str, filename: str) -> Path:
	return Path(__file__).resolve().parent / dirname / filename


def main(argv: Optional[List[str]] = None) -> int:
	parser = argparse.ArgumentParser(
		description=(
			"Create one IPC-2581 BomItem from an input XML in the input folder using "
			"EC_IPC.csv and append it into the BOM of Start.xml."
		)
	)
	parser.add_argument("input_xml", help="Input XML file name located in the input folder")
	args = parser.parse_args(argv)
	mapping_csv = _resolve_script_sidecar(DEFAULT_MAPPING_CSV)
	original_xml = _resolve_script_sidecar(DEFAULT_ORIGINAL_XML)
	input_xml = _resolve_script_child("input", args.input_xml)
	output_xml = _resolve_script_child("output", args.input_xml)

	if not mapping_csv.exists():
		raise SystemExit(f"Mapping CSV not found next to script: {mapping_csv}")
	if not original_xml.exists():
		raise SystemExit(f"Original XML not found next to script: {original_xml}")
	if not input_xml.exists():
		raise SystemExit(f"Input XML not found in input folder: {input_xml}")
	output_xml.parent.mkdir(parents=True, exist_ok=True)

	mappings = _read_mapping_csv(mapping_csv)
	input_values = _parse_input_values(input_xml)

	# Prefer namespace from original document when building elements
	original_tree = ET.parse(original_xml)
	original_root = original_tree.getroot()
	namespace = IPC2581_NS
	if original_root.tag.startswith("{") and "}" in original_root.tag:
		namespace = original_root.tag.split("}", 1)[0][1:]

	bom_item = _build_bom_item(input_values=input_values, mappings=mappings, namespace=namespace)
	out_tree = _append_bom_item(original_xml, bom_item)

	# Register namespaces for cleaner output
	ET.register_namespace("", namespace)
	ET.register_namespace("xsd", XSD_NS)
	ET.register_namespace("xsi", XSI_NS)

	_indent(out_tree.getroot())
	out_tree.write(output_xml, encoding="utf-8", xml_declaration=True)

	return 0


if __name__ == "__main__":
	raise SystemExit(main())

