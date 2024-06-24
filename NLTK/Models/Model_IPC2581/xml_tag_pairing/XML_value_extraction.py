import xml.etree.ElementTree as ET


def extract_and_print_tags(xml_file, output_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # egyedi tag-ek eltárolása
    tags = set()

    def traverse(node, output, level=0):
        tag = node.tag
        if '}' in tag:
            tag = tag.split('}', 1)[1]  # namespace kivétele
        tags.add(tag)

        attributes = ', '.join(node.attrib.keys())
        indentation = '\t' * level

        if node.text:
            text_content = node.text.strip()
        else:
            text_content = ""

            # tag és tartalom kiírása
        print(f"{tag}: {text_content}")
        output.write(f"{indentation}{tag}: {text_content}\n")

        for child in node:
            traverse(child, output, level+1)


    with open(output_file, 'w') as output:
        traverse(root, output)

#XML fájl elérési útja - át kell írni, hogy másik gépen is megtalálja
xml_file = r'C:\Users\user\AITIA\ah-ai-translation-poc\NLTK\Models\Model_EC\SAE_EC_DataModel.xml_0'
output_file = 'EC0_tags_and_values.txt'
extract_and_print_tags(xml_file, output_file)