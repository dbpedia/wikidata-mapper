# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import json
from datetime import datetime
from itertools import ifilterfalse

from mapper.wikidata import (
    get_property_ids, get_entities, get_properties_metadata
)


if __name__ == '__main__':
    pids = get_property_ids()
    print('Got %d Property IDs.' % len(pids))

    entities = get_entities(pids)
    print('Got entities.')

    # Some properties have "OBSOLETE" in their labels.
    # They will be deleted soon, so we shouldn't consider them in matching.
    def is_obsolete(entity):
        return 'labels' in entity and 'OBSOLETE' in entity['labels']['en']

    entities = list(ifilterfalse(is_obsolete, entities))

    metadata = get_properties_metadata(pids)
    print('Got metadata.')

    # Not every Property has metadata, so we merge into entities.
    for entity in entities:
        if entity['id'] in metadata:
            entity['meta'] = metadata[entity['id']]

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
    filename = 'wikidata_properties_%s.json' % now

    try:
        with open(filename, 'wb') as f:
            json.dump(entities, f)
    except Exception as e:
        print(e)
    else:
        print('Dump is ready. Filename:')
        print(filename)
