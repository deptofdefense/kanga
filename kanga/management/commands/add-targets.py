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

from kanga.models import Group, Target
from kanga.encoder import KangaEncoder
from kanga.reader import reader
from kanga.utils import normalize_phone_number


class Command(BaseCommand):
    help = 'Add targets'

    def add_arguments(self, parser):
        parser.add_argument(
            '--group',
            type=str,
            default=None,
            required=True,
            help='Name')
        parser.add_argument(
            '--phone-number-field',
            type=str,
            default=None,
            required=True,
            help='Phone number field')
        parser.add_argument(
            '--first-name-field',
            type=str,
            default=None,
            required=True,
            help='First name field')
        parser.add_argument(
            '--last-name-field',
            type=str,
            default=None,
            required=True,
            help='Last name field')
        parser.add_argument(
            '--path',
            type=str,
            default=None,
            required=True,
            help='Path')

    def handle(self, *args, **options):
        #
        p = options['path']
        group_name = options['group']
        first_name_field = options['first_name_field']
        last_name_field = options['last_name_field']
        phone_number_field = options['phone_number_field']
        #
        Target.objects.all().delete()
        #
        f, targets = reader(src=p, format='csv')
        #
        for target in targets:
            g = Group.objects.get(name=group_name)
            #
            ph = normalize_phone_number(target[phone_number_field])
            if ph[0] != "+":
                if len(ph) == 10:
                    ph = "+1" + ph
                elif len(ph) > 10:
                    ph = "+" + ph

            #
            Target.objects.create(
                first_name=target[first_name_field],
                last_name=target[last_name_field],
                group=g,
                phone_number=ph
            )
        #
        f.close()
        #
        targets = [t for t in Target.objects.all()]
        json.dump([model_to_dict(t) for t in targets], sys.stdout, cls=KangaEncoder)
