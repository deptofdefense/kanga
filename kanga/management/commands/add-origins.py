# =================================================================
#
# Work of the U.S. Department of Defense, Defense Digital Service.
# Released as open source under the MIT License.  See LICENSE file.
#
# =================================================================

import json
import sys

from django.core.management.base import BaseCommand
from django.forms.models import model_to_dict

from kanga.models import Account, Origin
from kanga.encoder import KangaEncoder
from kanga.utils import clean_phone_number


class Command(BaseCommand):
    help = 'Add origins'

    def add_arguments(self, parser):
        parser.add_argument(
            '--account',
            type=str,
            default=None,
            required=True,
            help='Name')
        parser.add_argument(
            '--path',
            type=str,
            default=None,
            required=True,
            help='Path')

    def handle(self, *args, **options):
        #
        account = options['account']
        p = options['path']
        #
        a = Account.objects.get(id=account)
        #
        Origin.objects.all().delete()
        #
        with open(p, 'r') as file:
            text = clean_phone_number(file.read())
            for line in text.splitlines():
                Origin.objects.create(
                    account=a,
                    phone_number="+1{}".format(line),
                    voice=True,
                    sms=True,
                    mms=True,
                    fax=True,
                    active=True)
        #
        origins = [o for o in Origin.objects.all()]
        json.dump([model_to_dict(o) for o in origins], sys.stdout, cls=KangaEncoder)
