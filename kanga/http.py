# =================================================================
#
# Work of the U.S. Department of Defense, Defense Digital Service.
# Released as open source under the MIT License.  See LICENSE file.
#
# =================================================================

from django.http import JsonResponse


def Response(data):
    r = JsonResponse(data)
    r["Access-Control-Allow-Origin"] = "*"
    r["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    r["Access-Control-Max-Age"] = "1000"
    r["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
    return r
