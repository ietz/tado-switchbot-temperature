import logging
import time
from typing import List, Dict

from switchbot_client import SwitchBotClient
from switchbot_client.devices import MeterPlusUs, MeterPlusJp

from tado_switchbot_temperature.config import settings, SyncDevice
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

            if abs(meter_temperature - zone.temperature) > 0.5:
                new_offset = meter_temperature - zone.temperature + zone.offset

                logger.info(f'Changing temperature offset in {zone.name} from {zone.offset:.02f} to {new_offset:.02f}')
                zone.offset = new_offset

        time.sleep(5 * 60)


def get_meters(sync_devices: List[SyncDevice]) -> Dict[str, MeterPlusUs | MeterPlusJp]:
    switchbot = SwitchBotClient(token=settings['switchbot.open_token'])
    meter_ids = set(sync_device['meter_id'] for sync_device in sync_devices)
    devices = {meter_id: switchbot.device(meter_id) for meter_id in meter_ids}

    for device in devices.values():
        if not isinstance(device, (MeterPlusUs, MeterPlusJp)):
            raise InvalidMeterError()

    return devices


class InvalidMeterError(Exception):
    pass


def print_sync_devices(sync_devices: List[SyncDevice], meters: Dict[str, MeterPlusUs | MeterPlusJp], zones: TadoZones):
    logger.info('Synchronizing the following devices')
    for sync_device in sync_devices:
        logger.info(f'meter = {meters[sync_device["meter_id"]].device_name} <-> zone = {zones[sync_device["zone_id"]].name}')
