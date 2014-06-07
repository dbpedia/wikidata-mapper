# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import bz2
import json
import os
from datetime import datetime
from itertools import ifilterfalse

import requests

from mapper.dbpedia import parse_ontology, get_labels


# TODO get latest version
ONTOLOGY_URL = 'http://downloads.dbpedia.org/3.9/dbpedia_3.9.owl.bz2'
EXPORTS_PATH = 'dbpedia-exports'
ONTOLOGY_FILENAME = 'dbpedia.owl'
ONTOLOGY_FILEPATH = os.path.join(EXPORTS_PATH, ONTOLOGY_FILENAME)
DUMPS_PATH = 'dumps'


def fetch_ontology():
    print('Downloading %s file.' % ONTOLOGY_URL)
    archive = requests.get(ONTOLOGY_URL).content

    if not os.path.exists(EXPORTS_PATH):
        os.mkdir(EXPORTS_PATH)

    # Unzip it
    with open(ONTOLOGY_FILEPATH, 'wb') as f:
        f.write(bz2.decompress(archive))
    print('Unzipped DBPedia ontology to %s file.' % ONTOLOGY_FILEPATH)


def make_dump(json_data, filename, message):
    if not os.path.exists(DUMPS_PATH):
        os.mkdir(DUMPS_PATH)

    filepath = os.path.join(DUMPS_PATH, filename)

    try:
        with open(filepath, 'wb') as f:
            json.dump(json_data, f)
    except Exception as e:
        print(e)
    else:
        print()
        print(message)
        print(filepath)


def get_description(entity):
    try:
        return entity['data']['comments']['en']
    except KeyError:
        return ''


if __name__ == '__main__':
    if not os.path.exists(ONTOLOGY_FILEPATH):
        fetch_ontology()

    ontology = parse_ontology(ONTOLOGY_FILEPATH)

    classes = [
        {
            'title': c['url'].split('/')[-1],
            'labels': get_labels(c),
            'description': get_description(c),
        }
        for c in ontology['classes']
    ]
    make_dump(
        classes,
        'dbpedia_classes.json',
        'Minimal dump of DBPedia classes is ready. Filename:',
    )

    properties = ontology['object_properties'] + ontology['datatype_properties']
    properties = [
        {
            'title': p['url'].split('/')[-1],
            'labels': get_labels(p),
            'description': get_description(p),
        }
        for p in properties
    ]
    make_dump(
        properties,
        'dbpedia_properties.json',
        'Minimal dump of DBPedia properties is ready. Filename:',
    )
