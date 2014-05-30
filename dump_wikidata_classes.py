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

from mapper.wikidata import get_class_entities


TAXONOMY_FILENAME = 'wikidata-taxonomy.nt'
EXPORTS_URL = 'http://tools.wmflabs.org/wikidata-exports/rdf/'
TAXONOMY_URL_TEMPLATE = 'http://tools.wmflabs.org/wikidata-exports/rdf/{date}/wikidata-taxonomy.nt.bz2'


if __name__ == '__main__':
    if not os.path.exists(TAXONOMY_FILENAME):
        # Download latest wikidata-taxonomy dump
        html = parse_html(requests.get(EXPORTS_URL).text.encode('utf8'))
        date_str = html.xpath('//td[@class="n"]/a')[-1].text
        taxonomy_url = TAXONOMY_URL_TEMPLATE.format(date=date_str)
        archive = requests.get(taxonomy_url).content
        print('Fetched wikidata-taxonomy.nt.bz2 file')

        # Unzip it
        with open(TAXONOMY_FILENAME, 'wb') as f:
            f.write(bz2.decompress(archive))
        print('Unzipped taxonomy to wikidata-taxonomy.nt file')

    try:
        entities = get_class_entities(TAXONOMY_FILENAME)
    except IOError as e:
        print(e)
        print(
            'Download latest wikidata-taxonomy.nt.bz2 file from '
            'http://tools.wmflabs.org/wikidata-exports/rdf/ and unzip it '
            'to %s' % os.path.dirname(os.path.realpath(__file__))
        )
    else:
        # Ignore missing Items
        entities = [e for e in entities if 'missing' in e]

        # Leave only English
        for entity in entities:
            # Leave only english
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

        now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M')
        filename = 'wikidata_classes_%s.json' % now

        try:
            with open(filename, 'wb') as f:
                json.dump(entities, f)
        except Exception as e:
            print(e)
        else:
            print('Dump is ready. Filename:')
            print(filename)
