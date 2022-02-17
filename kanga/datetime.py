# =================================================================
#
# Work of the U.S. Department of Defense, Defense Digital Service.
# Released as open source under the MIT License.  See LICENSE file.
#
# =================================================================

from datetime import datetime


def parse(str, timezone=None):
    d = None

    try:
        d = datetime.strptime(str, "%Y-%m-%dT%H:%M:%S.%fZ%z")
    except Exception:
        d = None

    if d is None:
        try:
            d = datetime.strptime(str, "%Y-%m-%dT%H:%M:%SZ%z")
        except Exception:
            d = None

    if d is None:
        try:
            d = datetime.strptime(str, "%Y-%m-%dT%H:%M:%S.%f")
            if timezone is not None:
                d = timezone.localize(d)
        except Exception:
            d = None

    if d is None:
        try:
            d = datetime.strptime(str, "%d %b %YT%H:%M:%S.%f")
            if timezone is not None:
                d = timezone.localize(d)
        except Exception:
            d = None

    if d is None:
        try:
            d = datetime.strptime(str, "%Y-%m-%dT%H:%M:%S")
            if timezone is not None:
                d = timezone.localize(d)
        except Exception as e:
            raise e

    return d


def fromtimestamp(ts):
    return datetime.fromtimestamp(ts)
