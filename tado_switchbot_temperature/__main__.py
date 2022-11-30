import argparse

from tado_switchbot_temperature.config import settings
from tado_switchbot_temperature.logging import configure_logging
from tado_switchbot_temperature.sync import sync

configure_logging(log_file_name=settings.get('log_file', None))
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(required=True)

parser_sync = subparsers.add_parser('sync')
parser_sync.set_defaults(func=sync)

args = parser.parse_args()
args.func()
