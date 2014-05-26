# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import json
import os
from datetime import datetime

from mapper.wikidata import get_class_entities


if __name__ == '__main__':
    # TODO? Download latest taxonomy dump, unzip it

    taxonomy_filename = 'wikidata-taxonomy.nt'
    try:
        entities = get_class_entities(taxonomy_filename)
    except IOError as e:
        print(e)
        print(
            'Download latest wikidata-taxonomy.nt.bz2 file from '
            'http://tools.wmflabs.org/wikidata-exports/rdf/ and unzip it '
            'to %s' % os.path.dirname(os.path.realpath(__file__))
        )
    else:
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
