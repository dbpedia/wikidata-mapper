# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import itertools

import Levenshtein

from . import dbpedia
from . import wikidata
from mapper.utils import normalize


def exact_label(d_entity, w_entity):
    d_labels = dbpedia.get_labels(d_entity)
    w_labels = wikidata.get_labels(w_entity)

    return 1 if any(d_label in w_labels for d_label in d_labels) else 0


def levenshtein(d_entity, w_entity):
    """Calculate similarity between every pair
    of English labels/aliases:
        l = sum length of two string
        d = Levenshtein distance between two strings
        similarity = (l - d) / l
    and return maximum value.
    """

    d_labels = [normalize(l) for l in dbpedia.get_labels(d_entity)]
    if not d_labels:
        return 0.0

    w_labels = [normalize(l) for l in wikidata.get_labels(w_entity)]
    if not w_labels:
        return 0.0

    pairs = itertools.product(d_labels, w_labels)
    return max(
        Levenshtein.ratio(d_label, w_label)
        for d_label, w_label in pairs
    )
