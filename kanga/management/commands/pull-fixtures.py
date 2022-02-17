# =================================================================
#
# Work of the U.S. Department of Defense, Defense Digital Service.
# Released as open source under the MIT License.  See LICENSE file.
#
# =================================================================

from __future__ import unicode_literals
import datetime
from django.core.management import call_command
from django.core.management.base import BaseCommand
from pathlib import Path

from kanga.utils import S3Mixin


class Command(BaseCommand, S3Mixin):

    def add_arguments(self, parser):
        parser.add_argument(
            '--objectkey',
            type=str,
            default=None,
            required=True,
            help='Object Key of remote fixture')

        parser.add_argument(
            '--fixturetype',
            type=str,
            default=None,
            required=True,
            help='Fixture type')

        parser.add_argument(
            '--dlfilename',
            type=str,
            default=None,
            required=False,
            help='Output filename of fixture')

    def load_fixture(self, fixture_file, fixture_type):
        command_name = f"add-{fixture_type}"
        call_command(command_name, path=fixture_file)

    def guarantee_dir(self, filepath):
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

    def handle(self, *args, **options):

        k = options['objectkey']
        t = options['fixturetype']
        f = options['dlfilename']

        accepted_types = ["origins", "targets"]
        try:
            assert t in accepted_types
        except Exception:
            raise Exception(f"unaccepted fixture type: \"{t}\"\naccepted types: {accepted_types}")

        if not f:
            f = f"./data/downloads/remote_dl_{t}_{datetime.datetime.now():%Y-%m-%d-%H-%M-%S}"

        print(f"objectkey:{k}\nfixturetype:{t}\ndlfilename:{f}")

        self.guarantee_dir(f)
        self.get_object(k, f)
        self.load_fixture(f, t)
