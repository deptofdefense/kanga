# =================================================================
#
# Work of the U.S. Department of Defense, Defense Digital Service.
# Released as open source under the MIT License.  See LICENSE file.
#
# =================================================================

import json
from datetime import datetime
import pytz
import sys
import traceback


class Logger:

    width = 60
    encoding = ""
    timezone = None

    def info(self, msg=None, fields=None):
        now = datetime.now(self.timezone)
        if fields is None:
            fields = {}
        if self.encoding == "json":
            data = dict(
                list(fields.items()) +
                list({"ts": now.isoformat(), "msg": msg}.items())
            )
            print(json.dumps(data))
        else:
            print(now.strftime("[ %H:%M:%S ] ")+" "+msg.ljust(self.width)+"    "+json.dumps(fields))

    def error(self, msg=None, fields=None):
        now = datetime.now(self.timezone)
        if fields is None:
            fields = {}
        if self.encoding == "json":
            data = dict(
                list(fields.items()) +
                list({"ts": now.isoformat(), "msg": msg, "traceback": (''.join(traceback.format_stack()))}.items())
            )
            print(json.dumps(data), file=sys.stderr)
        else:
            print(now.strftime("[ %H:%M:%S ] ")+" "+msg.ljust(self.width)+"    "+json.dumps(fields), file=sys.stderr)
            print(''.join(traceback.format_stack()), file=sys.stderr)

    def __init__(self, width=None, encoding=None, timezone=None):
        self.width = width
        self.encoding = encoding
        self.timezone = pytz.timezone(timezone)
