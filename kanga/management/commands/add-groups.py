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

from kanga.models import Group
from kanga.encoder import KangaEncoder


class Command(BaseCommand):
    help = 'Add groups'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            default=None,
            required=True,
            help='Path')

    def handle(self, *args, **options):
        #
        p = options['path']
        #
        Group.objects.all().delete()
        #
        with open(p, 'r') as file:
            text = file.read().replace(' ', '').replace('(', '').replace(')', '').replace('-', '')
            for line in text.splitlines():
                Group.objects.create(name=line)
        #
        groups = [o for o in Group.objects.all()]
        json.dump([model_to_dict(g) for g in groups], sys.stdout, cls=KangaEncoder)
