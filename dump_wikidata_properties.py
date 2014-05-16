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
    print('Got %d Properties.' % len(pids))

    entities = get_entities(pids)
    print('Got entities.')

    metadata = get_properties_metadata(pids)
    print('Got metadata.')

    # Not every Property has metadata, so we merge into entities.
    for pid, meta in metadata.viewitems():
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
