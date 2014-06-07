# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import itertools

import Levenshtein

from mapper.utils import normalize


def exact_label(d_entity, w_entity):
    d_labels = d_entity['labels']
    w_labels = w_entity['labels']

    return 1 if any(d_label in w_labels for d_label in d_labels) else 0


def levenshtein(d_entity, w_entity):
    """Calculate similarity between every pair
    of English labels/aliases:
        l = sum length of two string
        d = Levenshtein distance between two strings
        similarity = (l - d) / l
    and return maximum value.
    """

    d_labels = [normalize(l) for l in d_entity['labels']]
    if not d_labels:
        return 0.0

    w_labels = [normalize(l) for l in w_entity['labels']]
    if not w_labels:
        return 0.0

    pairs = itertools.product(d_labels, w_labels)
    return max(
        Levenshtein.ratio(d_label, w_label)
        for d_label, w_label in pairs
    )
