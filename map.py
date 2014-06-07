# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import csv
import json
import os

from mapper.matchers import exact_label
from mapper.utils import normalize


DUMPS_PATH = 'dumps'
MAPPINGS_PATH = 'mappings'
CSV_DELIMITER = str(';')

if __name__ == '__main__':
    print('Load dumps.')
    with open('dumps/dbpedia_properties.json') as f:
        d_properties = json.load(f)
    with open('dumps/dbpedia_classes.json') as f:
        d_classes = json.load(f)
    with open('dumps/wikidata_properties_minimal_en.json') as f:
        w_properties = json.load(f)
    with open('dumps/wikidata_classes_minimal_en.json') as f:
        w_classes = json.load(f)

    classes_candidates = []

    for c in w_properties:
        c['labels_'] = c['labels']
        c['labels'] = [normalize(l) for l in c['labels'] if normalize(l)]
    for c in d_properties:
        c['labels_'] = c['labels']
        c['labels'] = [normalize(l) for l in c['labels'] if normalize(l)]
    for c in w_classes:
        c['labels_'] = c['labels']
        c['labels'] = [normalize(l) for l in c['labels'] if normalize(l)]
    for c in d_classes:
        c['labels_'] = c['labels']
        c['labels'] = [normalize(l) for l in c['labels'] if normalize(l)]

    if not os.path.exists(MAPPINGS_PATH):
        os.mkdir(MAPPINGS_PATH)

    print('Map classes by exact_label matcher.')
    for dc in d_classes:
        for wc in w_classes:
            if exact_label(dc, wc):
                classes_candidates.append((dc, wc))

    filename = os.path.join(MAPPINGS_PATH, 'classes_candidates.csv')
    with open(filename, 'wb') as f:
        cw = csv.writer(f, delimiter=CSV_DELIMITER)

        for c in classes_candidates:
            row = [
                c[0]['description'],
                ', '.join(c[0]['labels_']),
                ', '.join(c[1]['labels_']),
                c[1]['description'],
                'http://mappings.dbpedia.org/index.php/OntologyClass:%s' % c[0]['title'],
                'http://wikidata.org/wiki/%s' % c[1]['title'],
            ]
            cw.writerow([column.encode('utf8') for column in row])
    print('Classes mapping file: %s.' % filename)

    print('Map properties by exact_label matcher.')
    properties_candidates = []
    for dp in d_properties:
        for wp in w_properties:
            if exact_label(dp, wp):
                properties_candidates.append((dp, wp))

    filename = os.path.join(MAPPINGS_PATH, 'properties_candidates.csv')
    with open(filename, 'wb') as f:
        cw = csv.writer(f, delimiter=CSV_DELIMITER)

        for c in properties_candidates:
            row = [
                c[0]['description'],
                ', '.join(c[0]['labels_']),
                ', '.join(c[1]['labels_']),
                c[1]['description'],
                ('http://mappings.dbpedia.org/index.php/OntologyProperty:%s' % c[0]['title']),
                'http://wikidata.org/wiki/%s' % c[1]['title'],
            ]
            cw.writerow([column.encode('utf8') for column in row])
    print('Properties mapping file: %s.' % filename)
