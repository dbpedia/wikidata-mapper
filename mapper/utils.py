# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)


import regex
import string
import time
import unicodedata
from itertools import izip_longest
from functools import wraps


def grouper(iterable, n):
    """Collect data into fixed-length chunks or blocks.
    grouper('ABCDEFG', 3) --> ABC DEF G
    """

    args = [iter(iterable)] * n
    return (
        tuple(x for x in group if x is not None)
        for group
        in izip_longest(*args)
    )


def retry(ExceptionToCheck, tries=4, delay=3, backoff=2, logger=None):
    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of
        exceptions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    """
    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            _tries, _delay = tries, delay
            while _tries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck as e:
                    msg = '%s, Retrying in %d seconds...' % (str(e), _delay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(_delay)
                    _tries -= 1
                    _delay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry


def normalize(term):
    """Normalize term strings for better matching.

    - Lowercase;
    - ASCII-folding;
    - replace all non-word characters with whitespace symbol;
    - strip leading and trailing whitespaces;
    - delete digits.

    >>> normalize(u'Chéri, fais-moi peur (1958)')
    u'cheri fais moi peur'
    """

    s = regex.sub(ur'[^\p{L}]+', ' ', term)
    s = ''.join(
        x for x in unicodedata.normalize('NFKD', s)
        if x in string.ascii_letters + ' '
    )
    return str(' '.join(w for w in s.lower().strip().split()))
