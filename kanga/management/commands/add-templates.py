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

from kanga.models import Template
from kanga.encoder import KangaEncoder
from kanga.reader import reader


class Command(BaseCommand):
    help = 'Add templates'

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
        Template.objects.all().delete()
        #
        #
        Template.objects.all().delete()
        #
        f, templates = reader(src=p, format='csv')
        #
        for template in templates:
            Template.objects.create(
                name=template['name'],
                body=template['body']
            )
        #
        f.close()
        #
        templates = [t for t in Template.objects.all()]
        json.dump([model_to_dict(t) for t in templates], sys.stdout, cls=KangaEncoder)
