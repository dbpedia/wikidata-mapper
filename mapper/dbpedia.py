# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from lxml.etree import parse


def parse_ontology(filename):
    with open(filename) as f:
        tree = parse(f)

    root = tree.getroot()

    class_tag = '{http://www.w3.org/2002/07/owl#}Class'
    classes = root.findall(class_tag)

    object_property_tag = '{http://www.w3.org/2002/07/owl#}ObjectProperty'
    object_properties = root.findall(object_property_tag)

    datatype_property_tag = '{http://www.w3.org/2002/07/owl#}DatatypeProperty'
    datatype_properties = root.findall(datatype_property_tag)

    return {
        'classes': [parse_entity(c) for c in classes],
        'object_properties': [parse_entity(op) for op in object_properties],
        'datatype_properties': [parse_entity(dp) for dp in datatype_properties],
    }


def clean_tag(tag):
    return tag[tag.find('}') + 1:]


def parse_entity(p):
    data = {'labels': {}, 'comments': {}}

    for c in p.getchildren():
        tag = clean_tag(c.tag)

        parsed = {clean_tag(k): v for k, v in c.attrib.iteritems()}

        if tag == 'label':
            data['labels'][parsed['lang']] = c.text
        elif tag == 'comment':
            data['comments'][parsed['lang']] = c.text
        elif tag in (
            'domain', 'range', 'equivalentProperty', 'equivalentClass',
            'subClassOf',
        ):
            data[tag] = parsed['resource']
        else:
            data[tag] = parsed

    return {
        'tag': clean_tag(p.tag),
        'url': p.attrib['{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about'],
        'data': data,
    }


def get_labels(entity, language='en'):
    try:
        return [unicode(entity['data']['labels'][language])]
    except KeyError:
        return [unicode(entity['url'].split('/')[-1])]
