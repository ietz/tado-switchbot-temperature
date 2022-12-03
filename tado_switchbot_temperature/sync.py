import datetime as dt
import logging
import time
from typing import List, Dict

from switchbot_client.devices import MeterPlus

from tado_switchbot_temperature.config import settings, SyncDevice
from tado_switchbot_temperature.ewma import EwmaSmoother
from tado_switchbot_temperature.meters import get_meters
from tado_switchbot_temperature.zones import TadoZones

logger = logging.getLogger(__name__)


def sync():
    sync_devices: List[SyncDevice] = settings['devices']
    meters = get_meters(sync_devices)
    zones = TadoZones.from_config()
    temperature_deltas = {
        zone.id: EwmaSmoother(halftime=dt.timedelta(seconds=settings.get('offset_smoothing_halftime', 45 * 60)))
        for zone in zones
    }

    print_sync_devices(sync_devices, meters, zones)

    while True:
        zones.update()

        for sync_device in sync_devices:
            zone = zones[sync_device['zone_id']]
            if zone.temperature is None:
                continue

            meter = meters[sync_device['meter_id']]
            meter_temperature = meter.temperature()

            logger.debug(f'{meter.device_name} reports a temperature of {meter_temperature} °C while tado reports {zone.temperature} C° in {zone.name}')

            temperature_delta = temperature_deltas[sync_device['zone_id']]
            temperature_delta.observe(meter_temperature - zone.temperature)

            if abs(temperature_delta.value) > settings.get('offset_update_threshold', 0.5):
                new_offset = temperature_delta.value + zone.offset
                logger.info(f'Changing the temperature offset in {zone.name} from {zone.offset:.02f} to {new_offset:.02f}')
                zone.offset = new_offset
                temperature_delta.zero()

        time.sleep(settings.get('probe_interval', 5 * 60))


def print_sync_devices(sync_devices: List[SyncDevice], meters: Dict[str, MeterPlus], zones: TadoZones):
    logger.info('Synchronizing the following devices')
    for sync_device in sync_devices:
        logger.info(f'meter = {meters[sync_device["meter_id"]].device_name} -> zone = {zones[sync_device["zone_id"]].name}')
