import argparse
import logging

from tado_switchbot_temperature.config import settings
from tado_switchbot_temperature.logging import configure_logging
from tado_switchbot_temperature.meters import print_available_meters
from tado_switchbot_temperature.sync import sync
from tado_switchbot_temperature.zones import print_available_zones

configure_logging(
    level=settings.get('logging.level', logging.INFO),
    file_name=settings.get('logging.file', None),
)

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(required=True)

parser_sync = subparsers.add_parser('sync')
parser_sync.set_defaults(func=sync)

parser_sync = subparsers.add_parser('zones')
parser_sync.set_defaults(func=print_available_zones)

parser_sync = subparsers.add_parser('meters')
parser_sync.set_defaults(func=print_available_meters)

args = parser.parse_args()
args.func()
