import xml.etree.ElementTree as ET


def extract_and_print_tags(xml_file):
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
        # tag és az attribútumainak kiírása
        print(f"{tag}: {attributes}")

        #output.write(f"{tag}: {attributes}\n") - régebbi indentáció nélküli fájlba írás
        output.write(indentation + tag + ": " + attributes + "\n")

        for child in node:
            traverse(child, output, level+1)


    with open(output_file, 'w') as output:
        traverse(root, output)


xml_file = r'C:\Users\user\AITIA\ah-ai-translation-poc\NLTK\Models\Model_IPC2581\FromXSDToXML_generation_ipc-2581C.xml'
output_file = 'IPC_tags_and_attributes.txt'
extract_and_print_tags(xml_file)
