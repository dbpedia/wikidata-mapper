# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import bz2
import json
import os
from datetime import datetime

import requests
from lxml.html import fromstring as parse_html

from mapper.wikidata import get_class_entities, get_labels

DUMPS_PATH = 'dumps'
TAXONOMY_FILEPATH = 'wikidata-exports/wikidata-taxonomy.nt'
EXPORTS_URL = 'http://tools.wmflabs.org/wikidata-exports/rdf/'
TAXONOMY_URL_TEMPLATE = 'http://tools.wmflabs.org/wikidata-exports/rdf/{date}/wikidata-taxonomy.nt.bz2'


def fetch_wikidata_taxonomy_dump():
    html = parse_html(requests.get(EXPORTS_URL).text.encode('utf8'))
    date_str = html.xpath('//td[@class="n"]/a')[-1].text
    taxonomy_url = TAXONOMY_URL_TEMPLATE.format(date=date_str)

    print('Downloading wikidata-taxonomy.nt.bz2 file.')
    archive = requests.get(taxonomy_url).content

    # Unzip it
    with open(TAXONOMY_FILEPATH, 'wb') as f:
        f.write(bz2.decompress(archive))
    print('Unzipped taxonomy to %s file' % TAXONOMY_FILEPATH)


def make_filename(suffix=None):
    now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M')
    filename_template = 'wikidata_classes_{datetime}{suffix}.json'
    return filename_template.format(
        datetime=now,
        suffix='' if suffix is None else ('_' + suffix),
    )


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
    if not os.path.exists(TAXONOMY_FILEPATH):
        fetch_wikidata_taxonomy_dump()

    print('Fetching classes\' entities from Wikidata.')
    entities = get_class_entities(TAXONOMY_FILEPATH)

    # Ignore missing Items
    entities = [e for e in entities if 'missing' not in e]

    # Dump all languages.
    filename = make_filename()
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
        if 'title' in entity:
            minimal_entities.append({
                'title': entity['title'],
                'labels': get_labels(entity),
            })

    filename = make_filename('minimal')
    make_dump(
        minimal_entities,
        filename,
        'Minimal dump is ready. Filename:',
    )
