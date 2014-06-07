# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import json
import os
from datetime import datetime
from itertools import ifilterfalse

from mapper.wikidata import (
    get_property_ids, get_entities, get_properties_metadata, get_labels
)


# Some properties have "OBSOLETE" in their labels.
# They will be deleted soon, so we shouldn't consider them in matching.
def is_obsolete(entity):
    return 'labels' in entity and 'OBSOLETE' in entity['labels']['en']


def make_filename(suffix=None):
    now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M')
    filename_template = 'wikidata_properties_{datetime}{suffix}.json'
    return filename_template.format(
        datetime=now,
        suffix='' if suffix is None else ('_' + suffix),
    )


def make_dump(json_data, filename, message):
    dump_directory = 'dumps'
    if not os.path.exists(dump_directory):
        os.mkdir(dump_directory)

    filepath = os.path.join(dump_directory, filename)

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
    pids = get_property_ids()
    print('Got %d Property IDs.' % len(pids))

    entities = get_entities(pids)
    print('Got entities.')

    entities = list(ifilterfalse(is_obsolete, entities))

    metadata = get_properties_metadata(pids)
    print('Got metadata.')

    # Not every Property has metadata, so we merge into entities.
    for entity in entities:
        if entity['id'] in metadata:
            entity['meta'] = metadata[entity['id']]

    # Dump all languages.
    make_dump(entities, make_filename(), 'Full dump is ready. Filename:')

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

    # Dump only English data.
    filename = make_filename('english')
    make_dump(entities, filename, 'English dump is ready. Filename:')

    # Prepare data for minimal dump.
    minimal_entities = []
    for entity in entities:
        try:
            desc = entity['descriptions']['en']
        except KeyError:
            desc = ''

        minimal_entities.append({
            'title': entity['title'],
            'labels': get_labels(entity),
            'description': desc,
        })

    # Dump {'title': ..., 'labels': [...]} structure.
    filename = make_filename('minimal')
    make_dump(minimal_entities, filename, 'Minimal dump is ready. Filename:')
