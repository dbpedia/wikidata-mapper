# -*- coding: utf-8 -*-

"""
Extracting Wikidata Properties and Items.
"""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import rdflib
import requests
from mwparserfromhell import parse as wikiparse
from rdflib.term import URIRef

from .utils import grouper, retry


WIKIDATA_API_URL = 'http://www.wikidata.org/w/api.php'
PROPERTIES_NAMESPACE = 120
APLIMIT = 500  # Limit for allpages query.
LIMIT = 50  # Limit for other queries.
DELIMITER = '|'

# TODO add logger


@retry(Exception, logger=None)
def request(action, **kwargs):
    """General Wikidata API call.
    Documentation and examples could be found here:
    http://www.wikidata.org/w/api.php
    """

    kwargs.update({
        'action': action,
        'format': kwargs.get('format', 'json'),
    })

    return requests.get(WIKIDATA_API_URL, params=kwargs).json()


def get_entities(pids):
    """wbgetentities method of API.
    Return the data for multiple Wikidata entities (e.g. Properties, Items).
    pids - list of strings, ids of pages (e.g. ['P551', 'Q3376']).
    """

    entities = []

    for i, pids_group in enumerate(grouper(pids, LIMIT)):
        response = request('wbgetentities', ids=DELIMITER.join(pids_group))
        entities.extend(response['entities'].viewvalues())
        # TODO use logger
        # TODO progress bar
        entities_left = len(pids) - (i + 1) * LIMIT
        if i % 10 == 0 and entities_left > 0:
            print('%d entities to get' % entities_left)

    # Transform {key1: value1, ...} to [value1, ...] where it's appropriate.
    for entity in entities:
        if 'aliases' in entity:
            for key, value in entity['aliases'].iteritems():
                entity['aliases'][key] = [a['value'] for a in value]

        if 'descriptions' in entity:
            for key, value in entity['descriptions'].iteritems():
                entity['descriptions'][key] = value['value']

        if 'labels' in entity:
            for key, value in entity['labels'].iteritems():
                entity['labels'][key] = value['value']

    return entities


def get_properties_talk_pages(pids):
    """pids - list of strings, ids of pages (e.g. ['P551', 'P69']).
    Return dict with content of talk pages ({id1: 'page1', id2: 'page2', ...}).
    """

    talk_pages = {}

    def get_pid(page):
        return page['title'].split(':')[1]

    def get_wikicode(page):
        return page['revisions'][0]['*']

    for i, pids_group in enumerate(grouper(pids, LIMIT)):
        response = request(
            'query',
            prop='revisions',
            rvprop='content',
            titles=DELIMITER.join(
                'Property_talk:%s' % pid
                for pid in pids_group
            ),
        )

        pages = [
            p for (pid, p) in response['query']['pages'].items()
            if int(pid) > 0  # API returns negative ids for missing pages
        ]

        talk_pages.update({
            get_pid(p): get_wikicode(p)
            for p in pages
        })

        # TODO use logger
        # TODO progress bar
        pages_left = len(pids) - (i + 1) * LIMIT
        if i % 10 and pages_left > 0:
            print('%d talk pages to get' % pages_left)

    return talk_pages


def parse_property_talk_page(page):
    wikicode = wikiparse(page)
    templates = wikicode.filter_templates()
    try:
        doc = [
            t for t in templates
            if t.name.strip() == 'Property documentation'
        ][0]
    except IndexError:
        doc = {}
    else:
        doc = {
            p.name.strip(): p.value.strip()
            for p in doc.params
            if p.value.strip()
        }

    constraints = [
        t for t in templates
        if t.name.strip().startswith('Constraint:')
    ]

    def get_template_name(template):
        return template.name.split(':')[1]

    def get_template_parameters(template):
        return {p.name.strip(): p.value.strip() for p in template.params}

    constraints = {
        get_template_name(c): get_template_parameters(c)
        for c in constraints
    }

    return {
        'doc': doc,
        'constraints': constraints,
    }


def get_properties_metadata(pids):
    """pids - list of strings, ids of pages (e.g. ['P551', 'P69']).
    Return dict {id1: {'raw': 'page1', 'meta': {...}}, ...}.
    """

    data = {}

    talk_pages = get_properties_talk_pages(pids)
    for pid, page in talk_pages.viewitems():
        meta = parse_property_talk_page(page)
        meta['raw'] = page
        data[pid] = meta

    return data


def get_property_ids(limit=None):
    """Return list of Wikidata Property ids.
    limit is a number of properties to get. Convenience for testing.
    """

    aplimit = limit if (limit is not None and limit < APLIMIT) else APLIMIT

    properties = []
    params = {
        'list': 'allpages',
        'apnamespace': PROPERTIES_NAMESPACE,
        'aplimit': aplimit,
    }

    while True:
        r = request('query', **params)
        properties.extend(r['query']['allpages'])

        stop_it = (
            'query-continue' not in r
            or
            limit is not None and len(properties) >= limit
        )

        if stop_it:
            break
        else:
            params['apfrom'] = r['query-continue']['allpages']['apcontinue']

    return [
        # p['title'] is like Property:P69, we want to get just P69
        p['title'].split(':')[1]
        for p in properties
    ]


def get_wikidata_class_ids(taxonomy_filename):
    """
    You can download taxonomy file here:
    http://tools.wmflabs.org/wikidata-exports/rdf
    """
    g = rdflib.Graph()
    taxonomy = g.parse(taxonomy_filename, format='nt')
    classes = list(s.split('/')[-1] for (s, p, o) in taxonomy.triples(
        (None, None, URIRef(u'http://www.w3.org/2002/07/owl#Class'))
    ))
    return [c for c in classes if c.startswith('Q')]


def get_class_entities(taxonomy_filename):
    class_ids = get_wikidata_class_ids(taxonomy_filename)
    entities = get_entities(class_ids)
    return entities


def get_labels(entity, language='en'):
    try:
        aliases = entity['aliases'][language]
    except KeyError:
        aliases = []

    try:
        aliases.append(entity['labels'][language])
    except KeyError:
        pass

    return aliases
