
import xml.etree.ElementTree as ET
import random
import os
import datetime as dt

# Path to your IPC-2581C schema file
schema_path = 'C:/Users/user/AITIA/ah-ai-translation-poc/NLTK/Models/Model_IPC2581/IPC-2581C.xsd'

# Parse the schema to get element and attribute details
tree = ET.parse(schema_path)
root = tree.getroot()

def generate_approval(datetime, person_ref):
    approval = ET.Element('Approval', attrib={
        'datetime': datetime,
        'personRef': person_ref
    })
    return approval


# Function to generate Arc XML element
def generate_arc(startX, startY, endX, endY, centerX, centerY, clockwise):
    arc = ET.Element('Arc', attrib={
        'startX': str(startX),
        'startY': str(startY),
        'endX': str(endX),
        'endY': str(endY),
        'centerX': str(centerX),
        'centerY': str(centerY),
        'clockwise': str(clockwise).lower()  # Convert boolean to lowercase string
    })
    line_desc = ET.SubElement(arc, 'LineDesc', attrib={
        'lineEnd': 'NONE',
        'lineWidth': '0',
        'lineProperty': 'SOLID'
    })
    return arc


# Function to generate AssemblyDrawing XML element
def generate_assembly_drawing(polygon_x, polygon_y, curve_centerX, curve_centerY, clockwise):
    assembly_drawing = ET.Element('AssemblyDrawing')

    outline = ET.SubElement(assembly_drawing, 'Outline')
    polygon = ET.SubElement(outline, 'Polygon')

    # Generate various elements within Polygon
    poly_begin = ET.SubElement(polygon, 'PolyBegin', attrib={
        'x': str(polygon_x),
        'y': str(polygon_y)
    })

    poly_step_curve = ET.SubElement(polygon, 'PolyStepCurve', attrib={
        'x': str(polygon_x),
        'y': str(polygon_y),
        'centerX': str(curve_centerX),
        'centerY': str(curve_centerY),
        'clockwise': str(clockwise).lower()
    })

    poly_step_segment = ET.SubElement(polygon, 'PolyStepSegment', attrib={
        'x': str(polygon_x),
        'y': str(polygon_y)
    })

    xform = ET.SubElement(polygon, 'Xform', attrib={
        'xOffset': '1',
        'yOffset': '1',
        'rotation': '0',
        'mirror': 'false',
        'faceUp': 'false',
        'scale': '1'
    })

    line_desc = ET.SubElement(polygon, 'LineDesc', attrib={
        'lineEnd': 'NONE',
        'lineWidth': '0',
        'lineProperty': 'SOLID'
    })

    fill_desc = ET.SubElement(polygon, 'FillDesc', attrib={
        'fillProperty': 'HOLLOW',
        'lineWidth': '0',
        'pitch1': '0',
        'pitch2': '0',
        'angle1': '0.00',
        'angle2': '0.00'
    })
    color = ET.SubElement(fill_desc, 'Color', attrib={
        'r': '0',
        'g': '0',
        'b': '0'
    })

    line_desc_outline = ET.SubElement(outline, 'LineDesc', attrib={
        'lineEnd': 'ROUND',
        'lineWidth': '1.7976931348623157E+308',
        'lineProperty': 'DOTTED'
    })

    marking_types = ['REFDES', 'PARTNAME', 'TARGET']
    for marking_type in marking_types:
        marking = ET.SubElement(assembly_drawing, 'Marking', attrib={
            'markingUsage': marking_type
        })
        location = ET.SubElement(marking, 'Location', attrib={
            'x': str(random.uniform(-100, 100)),  # Example of random value generation
            'y': str(random.uniform(-100, 100))
        })

    return assembly_drawing


def generate_avl_header(title, source, author, datetime, version, comment=None, mod_ref=None):
    avl_header = ET.Element('AvlHeader', attrib={
        'title': title,
        'source': source,
        'author': author,
        'datetime': datetime,
        'version': str(version),
        'comment': comment,
        'modRef': mod_ref
    })
    return avl_header


def generate_avl_item(oem_design_number):
    avl_item = ET.Element('AvlItem', attrib={
        'OEMDesignNumber': oem_design_number
    })
    return avl_item


def generate_avl_vmpn(evpl_vendor, evpl_mpn, qualified=False, chosen=False):
    avl_vmpn = ET.Element('AvlVmpn', attrib={
        'evplVendor': evpl_vendor,
        'evplMpn': evpl_mpn,
        'qualified': str(qualified).lower(),
        'chosen': str(chosen).lower()
    })
    return avl_vmpn


def generate_avl_mpn(name, rank=None, cost=None, moisture_sensitivity=None, availability=None, other=None):
    avl_mpn = ET.Element('AvlMpn', attrib={
        'name': name,
        'rank': str(rank) if rank is not None else None,
        'cost': str(cost) if cost is not None else None,
        'moistureSensitivity': moisture_sensitivity,
        'availability': str(availability).lower() if availability is not None else None,
        'other': other
    })
    return avl_mpn


def generate_bend_area(name, sequence_number=None, comment=None, circular_bend=None, outline=None):
    bend_area = ET.Element('BendArea', attrib={
        'name': name,
        'sequenceNumber': str(sequence_number) if sequence_number is not None else None,
        'comment': comment
    })

    if circular_bend is not None:
        bend_area.append(circular_bend)

    if outline is not None:
        bend_area.append(outline)

    return bend_area


def generate_bom_header(assembly, revision, affecting=None, step_refs=None):
    bom_header = ET.Element('BomHeader', attrib={
        'assembly': assembly,
        'revision': revision,
        'affecting': str(affecting).lower() if affecting is not None else None
    })

    if step_refs:
        for step_ref in step_refs:
            bom_header.append(step_ref)

    return bom_header


def generate_bom_item(oem_design_number_ref, quantity, category, bom_des=None, characteristics=None, spec_refs=None,
                      internal_part_number=None, description=None):
    bom_item = ET.Element('BomItem', attrib={
        'OEMDesignNumberRef': oem_design_number_ref,
        'quantity': quantity,
        'category': category,
        'internalPartNumber': internal_part_number,
        'description': description
    })

    if bom_des:
        for item in bom_des:
            bom_item.append(item)

    if characteristics:
        bom_item.append(characteristics)

    if spec_refs:
        for spec_ref in spec_refs:
            bom_item.append(spec_ref)

    return bom_item


def generate_ref_des(name, package_ref=None, populate=None, layer_ref=None, model_ref=None, tuning=None, firmware=None):
    ref_des = ET.Element('RefDes', attrib={
        'name': name,
        'packageRef': package_ref,
        'populate': str(populate).lower() if populate is not None else None,
        'layerRef': layer_ref,
        'modelRef': model_ref
    })

    if tuning:
        for item in tuning:
            ref_des.append(item)

    if firmware:
        for item in firmware:
            ref_des.append(item)

    return ref_des


def generate_mat_des(name, layer_ref=None):
    mat_des = ET.Element('MatDes', attrib={
        'name': name,
        'layerRef': layer_ref if layer_ref else ""
    })
    return mat_des


def generate_doc_des(name, layer_ref=None):
    doc_des = ET.Element('DocDes', attrib={
        'name': name,
        'layerRef': layer_ref if layer_ref else ""
    })
    return doc_des


def generate_tool_des(name, layer_ref=None):
    tool_des = ET.Element('ToolDes', attrib={
        'name': name,
        'layerRef': layer_ref if layer_ref else ""
    })
    return tool_des


# Function to generate FindDes XML element
def generate_find_des(number, layer_ref=None, model_ref=None):
    find_des = ET.Element('FindDes', attrib={
        'number': str(number),
        'layerRef': layer_ref if layer_ref else "",
        'modelRef': model_ref if model_ref else ""
    })
    return find_des


# Function to generate BomRef XML element
def generate_bom_ref(name):
    bom_ref = ET.Element('BomRef', attrib={'name': name})
    return bom_ref


# Function to generate Bom XML element
def generate_bom(name, bom_header, bom_items):
    bom = ET.Element('Bom', attrib={'name': name})
    bom.append(bom_header)
    for item in bom_items:
        bom.append(item)
    return bom


# Function to generate BoundingBox XML element
def generate_bounding_box(lower_left_x, lower_left_y, upper_right_x, upper_right_y):
    bounding_box = ET.Element('BoundingBox', attrib={
        'lowerLeftX': str(lower_left_x),
        'lowerLeftY': str(lower_left_y),
        'upperRightX': str(upper_right_x),
        'upperRightY': str(upper_right_y)
    })
    return bounding_box


# Function to generate Butterfly XML element
def generate_butterfly(shape, diameter=None, side=None):
    butterfly = ET.Element('Butterfly', attrib={'shape': shape})
    if diameter is not None:
        butterfly.set('diameter', str(diameter))
    if side is not None:
        butterfly.set('side', str(side))

    line_desc_group = ET.SubElement(butterfly, 'LineDescGroup')
    fill_desc_group = ET.SubElement(butterfly, 'FillDescGroup')

    return butterfly


# Function to generate CachedFirmware XML element
def generate_cached_firmware(hex_encoded_binary):
    cached_firmware = ET.Element('CachedFirmware', attrib={'hexEncodedBinary': hex_encoded_binary})
    return cached_firmware

# Function to generate CadData XML element
def generate_cad_data(layers, stackups, steps):
    cad_data = ET.Element('CadData')
    for layer in layers:
        cad_data.append(layer)
    for stackup in stackups:
        cad_data.append(stackup)
    for step in steps:
        cad_data.append(step)
    return cad_data

# Function to generate CadHeader XML element
def generate_cad_header(units, specs, change_recs):
    cad_header = ET.Element('CadHeader', attrib={'units': units})
    for spec in specs:
        cad_header.append(spec)
    for change_rec in change_recs:
        cad_header.append(change_rec)
    return cad_header

# Function to generate Certification XML element
def generate_certification(certification_status, certification_category=None):
    certification = ET.Element('Certification', attrib={'certificationStatus': certification_status})
    if certification_category is not None:
        certification.set('certificationCategory', certification_category)
    return certification

# Function to generate ChangeRec XML element
def generate_change_rec(datetime, person_ref, application, change, approvals=[]):
    change_rec = ET.Element('ChangeRec', attrib={
        'datetime': datetime,
        'personRef': person_ref,
        'application': application,
        'change': change
    })
    for approval in approvals:
        change_rec.append(approval)
    return change_rec

# Function to generate Characteristics XML element
def generate_characteristics(category, measured=[], ranged=[], enumerated=[], textual=[]):
    characteristics = ET.Element('Characteristics', attrib={'category': category})
    for m in measured:
        characteristics.append(m)
    for r in ranged:
        characteristics.append(r)
    for e in enumerated:
        characteristics.append(e)
    for t in textual:
        characteristics.append(t)
    return characteristics

# Function to generate Circle XML element
def generate_circle(diameter, line_desc_group=None, fill_desc_group=None):
    circle = ET.Element('Circle', attrib={'diameter': str(diameter)})
    if line_desc_group is not None:
        circle.append(line_desc_group)
    if fill_desc_group is not None:
        circle.append(fill_desc_group)
    return circle

# Function to generate CircularBend XML element
def generate_circular_bend(inner_side, inner_radius, inner_angle=None, bend_line=None):
    circular_bend = ET.Element('CircularBend', attrib={
        'innerSide': inner_side,
        'innerRadius': str(inner_radius)
    })
    if inner_angle is not None:
        circular_bend.set('innerAngle', str(inner_angle))
    if bend_line is not None:
        circular_bend.append(bend_line)
    return circular_bend


# Function to generate Color XML element
def generate_color(r, g, b):
    return ET.Element('Color', attrib={'r': str(r), 'g': str(g), 'b': str(b)})


# Function to generate ColorRef XML element
def generate_color_ref(id):
    return ET.Element('ColorRef', attrib={'id': id})


# Function to generate ColorTerm XML element
def generate_color_term(name, comment=None):
    color_term = ET.Element('ColorTerm', attrib={'name': name})
    if comment is not None:
        color_term.set('comment', comment)
    return color_term


# Function to generate Component XML element
def generate_component(part, layer_ref, mount_type, ref_des=None, mat_des=None, package_ref=None, model_ref=None,
                       weight=None, height=None, standoff=None, nonstandard_attributes=[], xform=None,
                       location=None, slot_cavity_ref=None, spec_refs=[]):
    component = ET.Element('Component', attrib={
        'part': part,
        'layerRef': layer_ref,
        'mountType': mount_type
    })
    if ref_des is not None:
        component.set('refDes', ref_des)
    if mat_des is not None:
        component.set('matDes', mat_des)
    if package_ref is not None:
        component.set('packageRef', package_ref)
    if model_ref is not None:
        component.set('modelRef', model_ref)
    if weight is not None:
        component.set('weight', str(weight))
    if height is not None:
        component.set('height', str(height))
    if standoff is not None:
        component.set('standoff', str(standoff))

    for attr in nonstandard_attributes:
        component.append(attr)
    if xform is not None:
        component.append(xform)
    if location is not None:
        component.append(location)
    if slot_cavity_ref is not None:
        component.append(slot_cavity_ref)
    for spec_ref in spec_refs:
        component.append(spec_ref)

    return component


# Function to generate Content XML element
def generate_content(role_ref, function_mode, step_refs=[], layer_refs=[], bom_refs=[], avl_ref=None,
                     dictionary_color=None, dictionary_line_desc=None, dictionary_fill_desc=None, dictionary_font=None,
                     dictionary_standard=None, dictionary_user=None, dictionary_firmware=None):
    content = ET.Element('Content', attrib={'roleRef': role_ref})
    content.append(function_mode)
    for step_ref in step_refs:
        content.append(step_ref)
    for layer_ref in layer_refs:
        content.append(layer_ref)
    for bom_ref in bom_refs:
        content.append(bom_ref)
    if avl_ref is not None:
        content.append(avl_ref)
    if dictionary_color is not None:
        content.append(dictionary_color)
    if dictionary_line_desc is not None:
        content.append(dictionary_line_desc)
    if dictionary_fill_desc is not None:
        content.append(dictionary_fill_desc)
    if dictionary_font is not None:
        content.append(dictionary_font)
    if dictionary_standard is not None:
        content.append(dictionary_standard)
    if dictionary_user is not None:
        content.append(dictionary_user)
    if dictionary_firmware is not None:
        content.append(dictionary_firmware)

    return content


# Function to generate Contour XML element
def generate_contour(polygon, cutouts=[]):
    contour = ET.Element('Contour')
    contour.append(polygon)
    for cutout in cutouts:
        contour.append(cutout)
    return contour


# Function to generate Criteria XML element
def generate_criteria(name, measurement_mode, comment=None, property=None, dfx_measurements=[]):
    criteria = ET.Element('Criteria', attrib={'name': name, 'measurementMode': measurement_mode})
    if comment is not None:
        criteria.set('comment', comment)
    if property is not None:
        criteria.append(property)
    for dfx_measurement in dfx_measurements:
        criteria.append(dfx_measurement)
    return criteria


# Function to generate Cutout XML element
def generate_cutout():
    return ET.Element('Cutout')


# Function to generate Dfx XML element
def generate_dfx(name, category, criteria=None, dfx_query=None):
    dfx = ET.Element('Dfx', attrib={'name': name, 'category': category})
    if criteria is not None:
        dfx.append(criteria)
    if dfx_query is not None:
        dfx.append(dfx_query)
    return dfx

# Function to generate DfxDetails XML element
def generate_dfx_details(feature_descriptions=[], markers=[], embedded_refs=[], external_refs=[]):
    dfx_details = ET.Element('DfxDetails')
    for feature_description in feature_descriptions:
        dfx_details.append(feature_description)
    for marker in markers:
        dfx_details.append(marker)
    for embedded_ref in embedded_refs:
        dfx_details.append(embedded_ref)
    for external_ref in external_refs:
        dfx_details.append(external_ref)
    return dfx_details

# Function to generate DfxMeasurement XML element
def generate_dfx_measurement(id, property, measurement_points, dfx_details=None, severity=None, comment=None):
    dfx_measurement = ET.Element('DfxMeasurement', attrib={'id': id})
    if severity is not None:
        dfx_measurement.set('severity', severity)
    if comment is not None:
        dfx_measurement.set('comment', comment)
    dfx_measurement.append(property)
    for point in measurement_points:
        dfx_measurement.append(point)
    if dfx_details is not None:
        dfx_measurement.append(dfx_details)
    return dfx_measurement

# Function to generate DfxQuery XML element
def generate_dfx_query(name, query, dfx_details=None, dfx_responses=[]):
    dfx_query = ET.Element('DfxQuery', attrib={'name': name, 'query': query})
    if dfx_details is not None:
        dfx_query.append(dfx_details)
    for response in dfx_responses:
        dfx_query.append(response)
    return dfx_query

# Function to generate DfxResponse XML element
def generate_dfx_response(response, dfx_details=None, dfx_measurement_ref=None, comment=None):
    dfx_response = ET.Element('DfxResponse', attrib={'response': response})
    if dfx_measurement_ref is not None:
        dfx_response.set('dfxMeasurementRef', dfx_measurement_ref)
    if comment is not None:
        dfx_response.set('comment', comment)
    if dfx_details is not None:
        dfx_response.append(dfx_details)
    return dfx_response

# Function to generate Diamond XML element
def generate_diamond(width, height, line_desc_group=None, fill_desc_group=None):
    diamond = ET.Element('Diamond', attrib={'width': str(width), 'height': str(height)})
    if line_desc_group is not None:
        diamond.append(line_desc_group)
    if fill_desc_group is not None:
        diamond.append(fill_desc_group)
    return diamond

# Function to generate DictionaryColor XML element
def generate_dictionary_color(entry_colors=[]):
    dictionary_color = ET.Element('DictionaryColor')
    for entry_color in entry_colors:
        dictionary_color.append(entry_color)
    return dictionary_color

# Function to generate DictionaryFirmware XML element
def generate_dictionary_firmware(entry_firmwares=[]):
    dictionary_firmware = ET.Element('DictionaryFirmware')
    for entry_firmware in entry_firmwares:
        dictionary_firmware.append(entry_firmware)
    return dictionary_firmware

# Function to generate DictionaryFont XML element
def generate_dictionary_font(units, entry_fonts=[]):
    dictionary_font = ET.Element('DictionaryFont', attrib={'units': units})
    for entry_font in entry_fonts:
        dictionary_font.append(entry_font)
    return dictionary_font

# Function to generate DictionaryLineDesc XML element
def generate_dictionary_line_desc(units, entry_line_descs=[]):
    dictionary_line_desc = ET.Element('DictionaryLineDesc', attrib={'units': units})
    for entry_line_desc in entry_line_descs:
        dictionary_line_desc.append(entry_line_desc)
    return dictionary_line_desc

# Function to generate DictionaryFillDesc XML element
def generate_dictionary_fill_desc(units, entry_fill_descs=[]):
    dictionary_fill_desc = ET.Element('DictionaryFillDesc', attrib={'units': units})
    for entry_fill_desc in entry_fill_descs:
        dictionary_fill_desc.append(entry_fill_desc)
    return dictionary_fill_desc

# Function to generate DictionaryStandard XML element
def generate_dictionary_standard(units, entry_standards=[]):
    dictionary_standard = ET.Element('DictionaryStandard', attrib={'units': units})
    for entry_standard in entry_standards:
        dictionary_standard.append(entry_standard)
    return dictionary_standard

# Function to generate DictionaryUser XML element
def generate_dictionary_user(units, entry_users=[]):
    dictionary_user = ET.Element('DictionaryUser', attrib={'units': units})
    for entry_user in entry_users:
        dictionary_user.append(entry_user)
    return dictionary_user

# Function to generate Donut XML element
def generate_donut(shape, outer_diameter, inner_diameter, line_desc_group=None, fill_desc_group=None):
    donut = ET.Element('Donut', attrib={'shape': shape, 'outerDiameter': str(outer_diameter), 'innerDiameter': str(inner_diameter)})
    if line_desc_group is not None:
        donut.append(line_desc_group)
    if fill_desc_group is not None:
        donut.append(fill_desc_group)
    return donut

# Function to generate Ecad XML element
def generate_ecad(name, cad_header, cad_data=None):
    ecad = ET.Element('Ecad', attrib={'name': name})
    ecad.append(cad_header)
    if cad_data is not None:
        ecad.append(cad_data)
    return ecad

# Function to generate EdgeCoupled XML element
def generate_edge_coupled(structure, line_width, line_gap, ref_planes=[]):
    edge_coupled = ET.Element('EdgeCoupled', attrib={'structure': structure})
    edge_coupled.append(line_width)
    edge_coupled.append(line_gap)
    for ref_plane in ref_planes:
        edge_coupled.append(ref_plane)
    return edge_coupled

# Function to generate Ellipse XML element
def generate_ellipse(width, height, line_desc_group=None, fill_desc_group=None):
    ellipse = ET.Element('Ellipse', attrib={'width': str(width), 'height': str(height)})
    if line_desc_group is not None:
        ellipse.append(line_desc_group)
    if fill_desc_group is not None:
        ellipse.append(fill_desc_group)
    return ellipse

# Function to generate EmbeddedRef XML element
def generate_embedded_ref(name, embedded_type, embedded_data):
    embedded_ref = ET.Element('EmbeddedRef', attrib={'name': name, 'embeddedType': embedded_type})
    embedded_ref.append(ET.Element('EmbeddedData', text=embedded_data))
    return embedded_ref

# Function to generate Enterprise XML element
def generate_enterprise(id, code, name=None, code_type=None, address1=None, address2=None, city=None, state_province=None, country=None, postal_code=None, phone=None, fax=None, email=None, url=None):
    enterprise = ET.Element('Enterprise', attrib={'id': id, 'code': code})
    if name is not None:
        enterprise.set('name', name)
    if code_type is not None:
        enterprise.set('codeType', code_type)
    if address1 is not None:
        enterprise.set('address1', address1)
    if address2 is not None:
        enterprise.set('address2', address2)
    if city is not None:
        enterprise.set('city', city)
    if state_province is not None:
        enterprise.set('stateProvince', state_province)
    if country is not None:
        enterprise.set('country', country)
    if postal_code is not None:
        enterprise.set('postalCode', postal_code)
    if phone is not None:
        enterprise.set('phone', phone)
    if fax is not None:
        enterprise.set('fax', fax)
    if email is not None:
        enterprise.set('email', email)
    if url is not None:
        enterprise.set('url', url)
    return enterprise


# Function to generate EntryColor XML element
def generate_entry_color(id, color):
    entry_color = ET.Element('EntryColor', attrib={'id': id})
    entry_color.append(color)
    return entry_color


# Function to generate EntryFirmware XML element
def generate_entry_firmware(id, cached_firmware):
    entry_firmware = ET.Element('EntryFirmware', attrib={'id': id})
    entry_firmware.append(cached_firmware)
    return entry_firmware


# Function to generate EntryFont XML element
def generate_entry_font(id, font_def):
    entry_font = ET.Element('EntryFont', attrib={'id': id})
    entry_font.append(font_def)
    return entry_font


# Function to generate EntryLineDesc XML element
def generate_entry_line_desc(id, line_desc):
    entry_line_desc = ET.Element('EntryLineDesc', attrib={'id': id})
    entry_line_desc.append(line_desc)
    return entry_line_desc


# Function to generate EntryFillDesc XML element
def generate_entry_fill_desc(id, fill_desc):
    entry_fill_desc = ET.Element('EntryFillDesc', attrib={'id': id})
    entry_fill_desc.append(fill_desc)
    return entry_fill_desc


# Function to generate EntryStandard XML element
def generate_entry_standard(id, standard_primitive):
    entry_standard = ET.Element('EntryStandard', attrib={'id': id})
    entry_standard.append(standard_primitive)
    return entry_standard


# Function to generate EntryUser XML element
def generate_entry_user(id, user_primitive):
    entry_user = ET.Element('EntryUser', attrib={'id': id})
    entry_user.append(user_primitive)
    return entry_user


# Function to generate Enumerated XML element
def generate_enumerated(definition_source=None, enumerated_characteristic_name=None,
                        enumerated_characteristic_value=None):
    enumerated = ET.Element('Enumerated')
    if definition_source:
        enumerated.set('definitionSource', definition_source)
    if enumerated_characteristic_name:
        enumerated.set('enumeratedCharacteristicName', enumerated_characteristic_name)
    if enumerated_characteristic_value:
        enumerated.set('enumeratedCharacteristicValue', enumerated_characteristic_value)
    return enumerated


# Function to generate ExternalRef XML element
def generate_external_ref(uri):
    return ET.Element('ExternalRef', text=uri)


# Function to generate Extrusion XML element
def generate_extrusion(start_height, height, feature, location, xform=None):
    extrusion = ET.Element('Extrusion', attrib={'startHeight': str(start_height), 'height': str(height)})
    extrusion.append(feature)
    extrusion.append(location)
    if xform:
        extrusion.append(xform)
    return extrusion


# Function to generate FeatureDescription XML element
def generate_feature_description(layer_ref=None, pin_ref=None, component_ref=None, package_ref=None, spec_ref=None,
                                 firmware_ref=None, padstack_def_ref=None, net_ref=None, stackup_ref=None, bom_ref=None,
                                 feature_object=None, comment=None, feature=None, xform=None, location=None):
    feature_description = ET.Element('FeatureDescription')
    if feature:
        feature_description.append(feature)
    if xform:
        feature_description.append(xform)
    if location:
        feature_description.append(location)

    if layer_ref:
        feature_description.set('layerRef', layer_ref)
    if pin_ref:
        feature_description.set('pinRef', pin_ref)
    if component_ref:
        feature_description.set('componentRef', component_ref)
    if package_ref:
        feature_description.set('packageRef', package_ref)
    if spec_ref:
        feature_description.set('specRef', spec_ref)
    if firmware_ref:
        feature_description.set('firmwareRef', firmware_ref)
    if padstack_def_ref:
        feature_description.set('padstackDefRef', padstack_def_ref)
    if net_ref:
        feature_description.set('netRef', net_ref)
    if stackup_ref:
        feature_description.set('stackupRef', stackup_ref)
    if bom_ref:
        feature_description.set('bomRef', bom_ref)
    if feature_object:
        feature_description.set('featureObject', feature_object)
    if comment:
        feature_description.set('comment', comment)

    return feature_description


def write_xml_to_file(root, filename):
    xmlstr = ET.tostring(root, encoding='unicode', method='xml')
    # Write to file with newline characters
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(xmlstr.replace('><', '>\n<'))


num_files = 100  # Number of XML files to generate
output_folder = 'generated_xmls'  # Folder to store generated XML files

# Create the output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

for i in range(num_files):
    current_date = dt.datetime.now()
    start_date = dt.datetime(1900, 1, 1)
    random_datetime = start_date + (random.random() * (current_date - start_date))
    datetime = random_datetime.strftime('%Y-%m-%dT%H:%M:%S%z')
    person_ref = "person" + str(i)
    names = ["Alpha", "Beta", "Gamma", "Delta"]
    random_name = random.choice(names)
    rank = random.uniform(1,5)
    cost = random.uniform(0,100)
    version = random.uniform(0.0, 10.0)
    sensitivity_values = ["Low", "Medium", "High"]
    sensitivity = random.choice(sensitivity_values)
    degrees = random.uniform(0, 360)

    startX = random.uniform(-100, 100)
    startY = random.uniform(-100, 100)
    endX = random.uniform(-100, 100)
    endY = random.uniform(-100, 100)
    centerX = random.uniform(-100, 100)
    centerY = random.uniform(-100, 100)
    clockwise = random.choice([True, False])

    polygon_x = random.uniform(-100, 100)
    polygon_y = random.uniform(-100, 100)
    curve_centerX = random.uniform(-100, 100)
    curve_centerY = random.uniform(-100, 100)
    clockwise_polygon = random.choice([True, False])

    # Generate XML elements
    approval_xml = generate_approval(datetime=datetime, person_ref=person_ref)
    arc_xml = generate_arc(startX=startX, startY=startY, endX=endX, endY=endY,
                           centerX=centerX, centerY=centerY, clockwise=clockwise)
    assembly_drawing_xml = generate_assembly_drawing(polygon_x=polygon_x, polygon_y=polygon_y,
                                                     curve_centerX=curve_centerX, curve_centerY=curve_centerY,
                                                     clockwise=clockwise_polygon)
    avl_header_xml = generate_avl_header(title="AVL Title", source="Source", author=random_name,
                                         datetime=datetime, version=version, comment=" ", mod_ref="ModRef")
    avl_item_xml = generate_avl_item(oem_design_number=f"OEM{i}")
    avl_vmpn_xml = generate_avl_vmpn(evpl_vendor=f"Vendor{i}", evpl_mpn=f"MPN{i}", qualified=clockwise, chosen=clockwise)
    avl_mpn_xml = generate_avl_mpn(name=random_name, rank=rank, cost=cost, moisture_sensitivity=sensitivity, availability=clockwise,
                                   other=" ")

    bend_area_xml = generate_bend_area(name=f"BendArea{i}", sequence_number=i, comment=" ")
    bom_header_xml = generate_bom_header(assembly=f"Assembly{i}", revision="RevA", affecting=clockwise)
    bom_item_xml = generate_bom_item(oem_design_number_ref=f"OEMDesignNumber{i}", quantity="10", category="CategoryA", internal_part_number=f"IPN{i}",
                                     description="Example Description")
    ref_des_xml = generate_ref_des(name=f"RefDes{i}", package_ref=f"Package{i}", populate=clockwise, layer_ref="Layer1",
                                   model_ref=f"Model{i}")
    mat_des_xml = generate_mat_des(name=f"MatDes{i}", layer_ref="Layer1")
    doc_des_xml = generate_doc_des(name=f"DocDes{i}", layer_ref="Layer1")
    tool_des_xml = generate_tool_des(name=f"ToolDes{i}", layer_ref="Layer1")
    find_des_xml = generate_find_des(number=i, layer_ref="Layer1", model_ref="ModelA")
    bom_ref_xml = generate_bom_ref(name=f"BomRef{i}")
    bom_xml = generate_bom(name=f"Bom{i}", bom_header=bom_header_xml,
                           bom_items=[bom_item_xml])  # Example: passing existing bom_header_xml and bom_item_xml
    bounding_box_xml = generate_bounding_box(lower_left_x=random.uniform(-100, 100),
                                             lower_left_y=random.uniform(-100, 100),
                                             upper_right_x=random.uniform(-100, 100),
                                             upper_right_y=random.uniform(-100, 100))
    butterfly_xml = generate_butterfly(shape="circle", diameter=random.uniform(0, 100), side=random.uniform(0, 100))
    cached_firmware_xml = generate_cached_firmware(hex_encoded_binary="ABC123DEF456")
    cad_data_xml = generate_cad_data(layers=[ET.Element('Layer') for _ in range(random.randint(1, 5))],
                                     stackups=[ET.Element('Stackup') for _ in range(random.randint(0, 3))],
                                     steps=[ET.Element('Step') for _ in range(random.randint(1, 5))])

    cad_header_xml = generate_cad_header(units="mm",
                                         specs=[ET.Element('Spec') for _ in range(random.randint(0, 3))],
                                         change_recs=[generate_change_rec(datetime=datetime,
                                                                          person_ref=person_ref,
                                                                          application="App",
                                                                          change="Change")
                                                      for _ in range(random.randint(0, 3))])

    certification_xml = generate_certification(certification_status="Certified",
                                               certification_category=random.choice(["Category1", "Category2", None]))

    characteristics_xml = generate_characteristics(category="Category",
                                                   measured=[ET.Element('Measured') for _ in
                                                             range(random.randint(0, 3))],
                                                   ranged=[ET.Element('Ranged') for _ in range(random.randint(0, 3))],
                                                   enumerated=[ET.Element('Enumerated') for _ in
                                                               range(random.randint(0, 3))],
                                                   textual=[ET.Element('Textual') for _ in range(random.randint(0, 3))])

    circle_xml = generate_circle(diameter=random.uniform(1, 100),
                                 line_desc_group=ET.Element('LineDescGroup') if random.choice([True, False]) else None,
                                 fill_desc_group=ET.Element('FillDescGroup') if random.choice([True, False]) else None)

    circular_bend_xml = generate_circular_bend(inner_side="Left",
                                               inner_radius=random.uniform(1, 50),
                                               inner_angle=random.uniform(0, 360) if random.choice(
                                                   [True, False]) else None,
                                               bend_line=ET.Element('BendLine'))
    color_xml = generate_color(r=random.randint(0, 255), g=random.randint(0, 255), b=random.randint(0, 255))
    color_ref_xml = generate_color_ref(id=f"ColorRef{i}")
    color_term_xml = generate_color_term(name=f"ColorName{i}",
                                         comment="This is a comment" if random.choice([True, False]) else None)

    component_xml = generate_component(part=f"Part{i}", layer_ref="Layer1", mount_type="Surface",
                                       ref_des=f"RefDes{i}", mat_des=f"MatDes{i}", package_ref=f"Package{i}",
                                       model_ref=f"Model{i}",
                                       weight=random.uniform(0, 10), height=random.uniform(0, 10),
                                       standoff=random.uniform(0, 10),
                                       nonstandard_attributes=[ET.Element('NonstandardAttribute') for _ in
                                                               range(random.randint(0, 3))],
                                       xform=ET.Element('Xform') if random.choice([True, False]) else None,
                                       location=ET.Element('Location'),
                                       slot_cavity_ref=ET.Element('SlotCavityRef') if random.choice(
                                           [True, False]) else None,
                                       spec_refs=[ET.Element('SpecRef') for _ in range(random.randint(0, 3))])

    content_xml = generate_content(role_ref="Role1", function_mode=ET.Element('FunctionMode'),
                                   step_refs=[ET.Element('StepRef') for _ in range(random.randint(0, 3))],
                                   layer_refs=[ET.Element('LayerRef') for _ in range(random.randint(0, 3))],
                                   bom_refs=[ET.Element('BomRef') for _ in range(random.randint(0, 3))],
                                   avl_ref=ET.Element('AvlRef') if random.choice([True, False]) else None,
                                   dictionary_color=ET.Element('DictionaryColor') if random.choice(
                                       [True, False]) else None,
                                   dictionary_line_desc=ET.Element('DictionaryLineDesc') if random.choice(
                                       [True, False]) else None,
                                   dictionary_fill_desc=ET.Element('DictionaryFillDesc') if random.choice(
                                       [True, False]) else None,
                                   dictionary_font=ET.Element('DictionaryFont') if random.choice(
                                       [True, False]) else None,
                                   dictionary_standard=ET.Element('DictionaryStandard') if random.choice(
                                       [True, False]) else None,
                                   dictionary_user=ET.Element('DictionaryUser') if random.choice(
                                       [True, False]) else None,
                                   dictionary_firmware=ET.Element('DictionaryFirmware') if random.choice(
                                       [True, False]) else None)

    contour_xml = generate_contour(polygon=ET.Element('Polygon'),
                                   cutouts=[generate_cutout() for _ in range(random.randint(0, 3))])

    criteria_xml = generate_criteria(name=f"Criteria{i}", measurement_mode="Mode1",
                                     comment="This is a comment" if random.choice([True, False]) else None,
                                     property=ET.Element('Property'),
                                     dfx_measurements=[ET.Element('DfxMeasurement') for _ in
                                                       range(random.randint(1, 3))])

    cutout_xml = generate_cutout()

    dfx_xml = generate_dfx(name=f"Dfx{i}", category="Category1",
                           criteria=criteria_xml if random.choice([True, False]) else None,
                           dfx_query=ET.Element('DfxQuery') if random.choice([True, False]) else None)

    dfx_details_xml = generate_dfx_details(
        feature_descriptions=[ET.Element('FeatureDescription') for _ in range(random.randint(0, 3))],
        markers=[ET.Element('Marker') for _ in range(random.randint(0, 3))],
        embedded_refs=[ET.Element('EmbeddedRef') for _ in range(random.randint(0, 3))],
        external_refs=[ET.Element('ExternalRef') for _ in range(random.randint(0, 3))]
    )

    dfx_measurement_xml = generate_dfx_measurement(
        id=f"Measurement{i}",
        property=ET.Element('Property'),
        measurement_points=[ET.Element('MeasurementPoint') for _ in range(random.randint(1, 5))],
        dfx_details=dfx_details_xml if random.choice([True, False]) else None,
        severity="High" if random.choice([True, False]) else None,
        comment="Measurement comment" if random.choice([True, False]) else None
    )

    dfx_query_xml = generate_dfx_query(
        name=f"Query{i}",
        query=f"Query text {i}",
        dfx_details=dfx_details_xml if random.choice([True, False]) else None,
        dfx_responses=[ET.Element('DfxResponse') for _ in range(random.randint(0, 3))]
    )

    dfx_response_xml = generate_dfx_response(
        response="Accepted",
        dfx_details=dfx_details_xml if random.choice([True, False]) else None,
        dfx_measurement_ref=f"MeasurementRef{i}" if random.choice([True, False]) else None,
        comment="Response comment" if random.choice([True, False]) else None
    )

    diamond_xml = generate_diamond(
        width=random.uniform(1, 10),
        height=random.uniform(1, 10),
        line_desc_group=ET.Element('LineDescGroup') if random.choice([True, False]) else None,
        fill_desc_group=ET.Element('FillDescGroup') if random.choice([True, False]) else None
    )

    dictionary_color_xml = generate_dictionary_color(
        entry_colors=[ET.Element('EntryColor') for _ in range(random.randint(0, 5))]
    )

    dictionary_firmware_xml = generate_dictionary_firmware(
        entry_firmwares=[ET.Element('EntryFirmware') for _ in range(random.randint(0, 5))]
    )

    dictionary_font_xml = generate_dictionary_font(
        units="mm",
        entry_fonts=[ET.Element('EntryFont') for _ in range(random.randint(0, 5))]
    )

    dictionary_line_desc_xml = generate_dictionary_line_desc(
        units="mm",
        entry_line_descs=[ET.Element('EntryLineDesc') for _ in range(random.randint(0, 5))]
    )

    dictionary_fill_desc_xml = generate_dictionary_fill_desc(
        units="mm",
        entry_fill_descs=[ET.Element('EntryFillDesc') for _ in range(random.randint(0, 5))]
    )

    dictionary_standard_xml = generate_dictionary_standard(
        units="mm",
        entry_standards=[ET.Element('EntryStandard') for _ in range(random.randint(0, 5))]
    )

    dictionary_user_xml = generate_dictionary_user(
        units="mm",
        entry_users=[ET.Element('EntryUser') for _ in range(random.randint(0, 5))]
    )

    donut_xml = generate_donut(
        shape="circle",
        outer_diameter=random.uniform(1, 10),
        inner_diameter=random.uniform(0.1, 5),
        line_desc_group=ET.Element('LineDescGroup') if random.choice([True, False]) else None,
        fill_desc_group=ET.Element('FillDescGroup') if random.choice([True, False]) else None
    )

    ecad_xml = generate_ecad(
        name=f"EcadName{i}",
        cad_header=ET.Element('CadHeader'),
        cad_data=ET.Element('CadData') if random.choice([True, False]) else None
    )

    edge_coupled_xml = generate_edge_coupled(
        structure="microstrip",
        line_width=ET.Element('LineWidth'),
        line_gap=ET.Element('LineGap'),
        ref_planes=[ET.Element('RefPlane') for _ in range(random.randint(0, 2))]
    )

    ellipse_xml = generate_ellipse(
        width=random.uniform(1, 10),
        height=random.uniform(1, 10),
        line_desc_group=ET.Element('LineDescGroup') if random.choice([True, False]) else None,
        fill_desc_group=ET.Element('FillDescGroup') if random.choice([True, False]) else None
    )

    embedded_ref_xml = generate_embedded_ref(
        name=f"EmbeddedRefName{i}",
        embedded_type="image",
        embedded_data="binarydata"
    )

    enterprise_xml = generate_enterprise(
        id=f"EnterpriseID{i}",
        code=f"EnterpriseCode{i}",
        name=f"EnterpriseName{i}" if random.choice([True, False]) else None,
        code_type="internal" if random.choice([True, False]) else None,
        address1="1234 Main St" if random.choice([True, False]) else None,
        address2="Suite 100" if random.choice([True, False]) else None,
        city="SomeCity" if random.choice([True, False]) else None,
        state_province="CA" if random.choice([True, False]) else None,
        country="US" if random.choice([True, False]) else None,
        postal_code="12345" if random.choice([True, False]) else None,
        phone="123-456-7890" if random.choice([True, False]) else None,
        fax="098-765-4321" if random.choice([True, False]) else None,
        email="info@example.com" if random.choice([True, False]) else None,
        url="http://example.com" if random.choice([True, False]) else None
    )

    entry_color_xml = generate_entry_color(
        id=f"ColorID{i}",
        color=ET.Element('Color')
    )

    entry_firmware_xml = generate_entry_firmware(
        id=f"FirmwareID{i}",
        cached_firmware=ET.Element('CachedFirmware')
    )

    entry_font_xml = generate_entry_font(
        id=f"FontID{i}",
        font_def=ET.Element('FontDef')
    )

    entry_line_desc_xml = generate_entry_line_desc(
        id=f"LineDescID{i}",
        line_desc=ET.Element('LineDesc')
    )

    entry_fill_desc_xml = generate_entry_fill_desc(
        id=f"FillDescID{i}",
        fill_desc=ET.Element('FillDesc')
    )

    entry_standard_xml = generate_entry_standard(
        id=f"StandardID{i}",
        standard_primitive=ET.Element('StandardPrimitive')
    )

    entry_user_xml = generate_entry_user(
        id=f"UserID{i}",
        user_primitive=ET.Element('UserPrimitive')
    )

    enumerated_xml = generate_enumerated(
        definition_source="ExampleSource",
        enumerated_characteristic_name="ExampleName",
        enumerated_characteristic_value="ExampleValue"
    )

    external_ref_xml = generate_external_ref(
        uri=f"http://example.com/resource{i}"
    )

    extrusion_xml = generate_extrusion(
        start_height=random.uniform(0, 10),
        height=random.uniform(0, 10),
        feature=ET.Element('Feature'),
        location=ET.Element('Location'),
        xform=ET.Element('Xform') if random.choice([True, False]) else None
    )

    feature_description_xml = generate_feature_description(
        layer_ref=f"LayerRef{i}" if random.choice([True, False]) else None,
        pin_ref=f"PinRef{i}" if random.choice([True, False]) else None,
        component_ref=f"ComponentRef{i}" if random.choice([True, False]) else None,
        package_ref=f"PackageRef{i}" if random.choice([True, False]) else None,
        spec_ref=f"SpecRef{i}" if random.choice([True, False]) else None,
        firmware_ref=f"FirmwareRef{i}" if random.choice([True, False]) else None,
        padstack_def_ref=f"PadstackDefRef{i}" if random.choice([True, False]) else None,
        net_ref=f"NetRef{i}" if random.choice([True, False]) else None,
        stackup_ref=f"StackupRef{i}" if random.choice([True, False]) else None,
        bom_ref=f"BomRef{i}" if random.choice([True, False]) else None,
        feature_object="ObjectType" if random.choice([True, False]) else None,
        comment="This is a comment." if random.choice([True, False]) else None,
        feature=ET.Element('Feature') if random.choice([True, False]) else None,
        xform=ET.Element('Xform') if random.choice([True, False]) else None,
        location=ET.Element('Location') if random.choice([True, False]) else None
    )

    # Merge all XML elements into one root element
    root = ET.Element('Root', xmlns="http://webstds.ipc.org/2581")
    root.append(approval_xml)
    root.append(arc_xml)
    root.append(assembly_drawing_xml)
    root.append(avl_header_xml)
    root.append(avl_item_xml)
    root.append(avl_vmpn_xml)
    root.append(avl_mpn_xml)
    root.append(bend_area_xml)
    root.append(bom_header_xml)
    root.append(bom_item_xml)
    root.append(ref_des_xml)
    root.append(mat_des_xml)
    root.append(doc_des_xml)
    root.append(tool_des_xml)
    root.append(find_des_xml)
    root.append(bom_ref_xml)
    root.append(bom_xml)
    root.append(bounding_box_xml)
    root.append(butterfly_xml)
    root.append(cached_firmware_xml)
    root.append(cad_data_xml)
    root.append(cad_header_xml)
    root.append(certification_xml)
    root.append(characteristics_xml)
    root.append(circle_xml)
    root.append(circular_bend_xml)
    root.append(color_xml)
    root.append(color_ref_xml)
    root.append(color_term_xml)
    root.append(component_xml)
    root.append(content_xml)
    root.append(contour_xml)
    root.append(criteria_xml)
    root.append(cutout_xml)
    root.append(dfx_xml)
    root.append(dfx_details_xml)
    root.append(dfx_measurement_xml)
    root.append(dfx_query_xml)
    root.append(dfx_response_xml)
    root.append(diamond_xml)
    root.append(dictionary_color_xml)
    root.append(dictionary_firmware_xml)
    root.append(dictionary_font_xml)
    root.append(dictionary_line_desc_xml)
    root.append(dictionary_fill_desc_xml)
    root.append(dictionary_standard_xml)
    root.append(dictionary_user_xml)
    root.append(donut_xml)
    root.append(ecad_xml)
    root.append(edge_coupled_xml)
    root.append(ellipse_xml)
    root.append(embedded_ref_xml)
    root.append(enterprise_xml)
    root.append(entry_color_xml)
    root.append(entry_firmware_xml)
    root.append(entry_font_xml)
    root.append(entry_line_desc_xml)
    root.append(entry_fill_desc_xml)
    root.append(entry_standard_xml)
    root.append(entry_user_xml)
    root.append(enumerated_xml)
    root.append(external_ref_xml)
    root.append(extrusion_xml)
    root.append(feature_description_xml)

    # Write the merged XML to file
    filename = os.path.join(output_folder, f'generated_file_{i}.xml')
    write_xml_to_file(root, filename)

print(f'{num_files} XML files generated successfully in folder: {output_folder}')

