import logging
import time
from typing import List, Dict

from switchbot_client.devices import MeterPlusUs, MeterPlusJp

from tado_switchbot_temperature.config import settings, SyncDevice
from tado_switchbot_temperature.meters import get_meters
from tado_switchbot_temperature.zones import TadoZones

logger = logging.getLogger(__name__)


def sync():
    sync_devices: List[SyncDevice] = settings['devices']
    meters = get_meters(sync_devices)
    zones = TadoZones.from_config()

    print_sync_devices(sync_devices, meters, zones)

    while True:
        zones.update()

        for sync_device in sync_devices:
            zone = zones[sync_device['zone_id']]
            if zone.temperature is None:
                continue

            meter = meters[sync_device['meter_id']]
            meter_temperature = meter.temperature()

            logger.info(f'{meter.device_name} reports a temperature of {meter_temperature} °C while tado reports {zone.temperature} C° in {zone.name}')

            if abs(meter_temperature - zone.temperature) > settings.get('offset_threshold', 0.5):
                new_offset = meter_temperature - zone.temperature + zone.offset

                logger.info(f'Changing temperature offset in {zone.name} from {zone.offset:.02f} to {new_offset:.02f}')
                zone.offset = new_offset

        time.sleep(settings.get('sync_interval', 5 * 60))


def print_sync_devices(sync_devices: List[SyncDevice], meters: Dict[str, MeterPlusUs | MeterPlusJp], zones: TadoZones):
    logger.info('Synchronizing the following devices')
    for sync_device in sync_devices:
        logger.info(f'meter = {meters[sync_device["meter_id"]].device_name} <-> zone = {zones[sync_device["zone_id"]].name}')
