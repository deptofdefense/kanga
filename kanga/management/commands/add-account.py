# =================================================================
#
# Work of the U.S. Department of Defense, Defense Digital Service.
# Released as open source under the MIT License.  See LICENSE file.
#
# =================================================================

import json
import sys
import uuid

from django.core.management.base import BaseCommand
from django.forms.models import model_to_dict

from kanga.models import Account
from kanga.encoder import KangaEncoder


class Command(BaseCommand):
    help = 'Add account'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument(
            '--name',
            type=str,
            default=None,
            required=True,
            help='Name')
        parser.add_argument(
            '--sid',
            type=str,
            default=None,
            required=True,
            help='SID')
        parser.add_argument(
            '--auth-token',
            type=str,
            default=None,
            required=True,
            help='Auth Token')

    def handle(self, *args, **options):
        #
        name = options['name']
        sid = options['sid']
        auth_token = options['auth_token']
        #
        u = uuid.uuid4()
        Account.objects.create(uuid=u, name=name, sid=sid, auth_token=auth_token, active=True)
        #
        json.dump(model_to_dict(Account.objects.get(uuid=u)), sys.stdout, cls=KangaEncoder)
