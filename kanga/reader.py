# =================================================================
#
# Work of the U.S. Department of Defense, Defense Digital Service.
# Released as open source under the MIT License.  See LICENSE file.
#
# =================================================================

import csv
import gzip


def reader(src=None, format=None, compression=None):
    if format == "csv":
        if compression == "gzip":
            f = gzip.open(src, 'rt')
            return f, csv.DictReader(f)
        else:
            f = open(src, 'rt')
            return f, csv.DictReader(f)
