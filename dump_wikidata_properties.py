# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import pickle
from datetime import datetime

from mapper.wikidata import (
    get_property_ids, get_entities, get_properties_metadata
)


if __name__ == '__main__':
    pids = get_property_ids()
    print('Got %d Property IDs.' % len(pids))

    entities = get_entities(pids)
    print('Got entities.')

    obsolete_property_ids = []
    for pid, entity in entities.viewitems():
        if 'labels' in entity and 'OBSOLETE' in entity['labels']['en']:
            obsolete_property_ids.append(pid)

    for pid in obsolete_property_ids:
        del entities[pid]

    metadata = get_properties_metadata(pids)
    print('Got metadata.')

    # Not every Property has metadata, so we merge into entities.
    for pid, meta in metadata.viewitems():
        if pid in entities:
            entities[pid]['meta'] = meta

    now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M')
    filename = 'wikidata_properties_%s.pickle' % now

    try:
        with open(filename, 'wb') as f:
            pickle.dump(entities, f)
    except Exception as e:
        print(e)
    else:
        print('Dump is ready. Filename:')
        print(filename)
