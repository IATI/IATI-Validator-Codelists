import os
import json
from lxml import etree as ET

def find_equivalent_mapping_element(mapping, rule_mappings):
    path = mapping.find('path').text
    if (mapping.find('condition') is not None):
        condition = mapping.find('condition').text
    else:
        condition = ""
    name = mapping.find('codelist').attrib['ref']
    for rule_mapping in rule_mappings.getroot().xpath('//mapping'):
        rule_map_path = rule_mapping.find('path').text
        if (rule_mapping.find('condition') is not None):
            rule_condition = rule_mapping.find('condition').text
        else:
            rule_condition = ""
        rule_name = rule_mapping.find('codelist').attrib['ref']
        if rule_map_path == path and rule_condition == condition and rule_name == name:
            return rule_mapping
    return None


def mapping_to_codelist_rules(mappings, rule_mappings):
    data = dict()
    for mapping in mappings.getroot().xpath('//mapping'):
        path_ref = mapping.find('path').text.split('/@')
        # handle edge case of path:
        #   '//iati-activity/crs-add/channel-code/text()'
        if len(path_ref) != 2:
            split = mapping.find('path').text.rpartition('/')
            path_ref = [split[0], split[2]]
        path = path_ref[0]
        # change to direct reference paths
        path = path.replace('//iati-activities', '/iati-activities')
        path = path.replace('//iati-activity', '/iati-activities/iati-activity')
        path = path.replace('//iati-organisations', '/organisations')
        path = path.replace('//iati-organisation', '/iati-organisations/iati-organisation')

        attribute = path_ref[1]
        name = mapping.find('codelist').attrib['ref']
        file_name = name + '.xml'

        # get allowed codes into a list
        codelist = ET.parse(os.path.join('IATI-Codelists' ,'combined-xml', file_name))
        codes = codelist.getroot().xpath('//code')
        allowedCodes = []
        for code in codes:
            allowedCodes.append(code.text)

        existingPath = data.get(path) is not None
        existingPathAtr = ''
        if existingPath:
            existingPathAtr = data[path].get(attribute) is not None
        out = {
            path: {
                attribute: {
                }
            }
        }
        if (mapping.find('condition') is not None):
            # parse condition xpath
            condition = mapping.find('condition').text
            parts = condition.split(' or ')
            splitfirst = parts[0].split(' = ')
            link = splitfirst[0].lstrip('@')
            linkValue = splitfirst[1].strip("'")
            # import pdb; pdb.set_trace() # debugging code

            defaultLink = ''
            if len(parts) > 1:
                defaultLink = linkValue

            if not existingPath or not existingPathAtr:
                out[path][attribute]["conditions"] = {}
                out[path][attribute]["conditions"]["mapping"] = {}
                out[path][attribute]["conditions"]["linkedAttribute"] = link
            elif data[path][attribute].get("conditions") is None:
                out[path][attribute]["conditions"] = {}
                out[path][attribute]["conditions"]["mapping"] = {}
                out[path][attribute]["conditions"]["linkedAttribute"] = link
            else:
                out[path][attribute]["conditions"] = data[path][attribute]["conditions"]
            if defaultLink:
                out[path][attribute]["conditions"]["defaultLink"] = defaultLink

            out[path][attribute]["conditions"]["mapping"][linkValue] = {"codelist": name, "allowedCodes": allowedCodes}
        else:
            out[path][attribute]["codelist"] = name
            out[path][attribute]["allowedCodes"] = allowedCodes

        # add validation rules
        rule_mapping = find_equivalent_mapping_element(mapping, rule_mappings)
        if rule_mapping is not None:
            validation_rules = rule_mapping.find('validation-rules')
            if validation_rules is not None:
                for validation_rule in validation_rules:
                    for child in validation_rule:
                        if mapping.find('condition') is not None:
                            out[path][attribute]["conditions"]["mapping"][linkValue][child.tag] = child.text
                        else:
                            out[path][attribute][child.tag] = child.text
        if existingPath:
            data[path][attribute] = out[path][attribute]
        else:
            data.update(out)
    return data


rule_mappings = ET.parse('rule_mapping.xml')
mappings = ET.parse('IATI-Codelists/mapping.xml')
with open('codelist_rules.json', 'w') as fp:
    data = mapping_to_codelist_rules(mappings, rule_mappings)
    json.dump(data, fp, indent=2)
