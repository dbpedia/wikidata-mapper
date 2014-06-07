# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import bz2
import json
import os

import requests
from lxml.html import fromstring as parse_html

from mapper.wikidata import get_class_entities, get_labels

DUMPS_PATH = 'dumps'
EXPORTS_PATH = 'wikidata-exports'
TAXONOMY_FILENAME = 'wikidata-taxonomy.nt'
TAXONOMY_FILEPATH = os.path.join(EXPORTS_PATH, TAXONOMY_FILENAME)
EXPORTS_URL = 'http://tools.wmflabs.org/wikidata-exports/rdf'
TAXONOMY_URL_TEMPLATE = EXPORTS_URL + '/{date}/wikidata-taxonomy.nt.bz2'


def fetch_wikidata_taxonomy_dump():
    html = parse_html(requests.get(EXPORTS_URL).text.encode('utf8'))
    date_str = html.xpath('//td[@class="n"]/a')[-1].text
    taxonomy_url = TAXONOMY_URL_TEMPLATE.format(date=date_str)

    print('Downloading wikidata-taxonomy.nt.bz2 file.')
    archive = requests.get(taxonomy_url).content

    if not os.path.exists(EXPORTS_PATH):
        os.mkdir(EXPORTS_PATH)

    # Unzip it
    with open(TAXONOMY_FILEPATH, 'wb') as f:
        f.write(bz2.decompress(archive))
    print('Unzipped taxonomy to %s file.' % TAXONOMY_FILEPATH)


def make_filename(suffix):
    return 'wikidata_classes_%s.json' % suffix


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


if __name__ == '__main__':
    # TODO Check if we have latest taxonomy export
    if not os.path.exists(TAXONOMY_FILEPATH):
        fetch_wikidata_taxonomy_dump()

    print('Fetching classes\' entities from Wikidata.')
    entities = get_class_entities(TAXONOMY_FILEPATH)

    # Ignore missing Items
    entities = [e for e in entities if 'missing' not in e]

    # Dump all languages.
    filename = make_filename('full')
    make_dump(entities, filename, 'Full dump is ready. Filename:')

    # Prepare data for English dump.
    for entity in entities:
        if 'aliases' in entity:
            for language in entity['aliases'].keys():
                if language != 'en':
                    del entity['aliases'][language]

        if 'descriptions' in entity:
            for language in entity['descriptions'].keys():
                if language != 'en':
                    del entity['descriptions'][language]

        if 'labels' in entity:
            for language in entity['labels'].keys():
                if language != 'en':
                    del entity['labels'][language]

        if 'sitelinks' in entity:
            for language in entity['sitelinks'].keys():
                if language != 'enwiki':
                    del entity['sitelinks'][language]

    filename = make_filename('english')
    make_dump(entities, filename, 'English dump is ready. Filename:')

    # Prepare data for minimal dump.
    minimal_entities = []
    for entity in entities:
        try:
            desc = entity['descriptions']['en']
        except KeyError:
            desc = ''

        if 'title' in entity:
            minimal_entities.append({
                'title': entity['title'],
                'labels': get_labels(entity),
                'description': desc,
            })

    filename = make_filename('minimal_en')
    make_dump(
        minimal_entities,
        filename,
        'Minimal dump is ready. Filename:',
    )
