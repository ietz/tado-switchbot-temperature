import logging
from typing import List, Dict

from PyTado.interface import Tado
from switchbot_client import SwitchBotClient
from switchbot_client.devices import MeterPlusUs, MeterPlusJp

from tado_switchbot_temperature.config import settings, SyncDevice
from tado_switchbot_temperature.zones import TadoZones

logger = logging.getLogger(__name__)


def sync():
    sync_devices: List[SyncDevice] = settings['devices']

    meters = get_meters(sync_devices)

    tado = Tado(username=settings['tado.username'], password=settings['tado.password'])
    zones = TadoZones(tado)
    zones.update()

    for sync_device in sync_devices:
        meter = meters[sync_device['meter_id']]
        meter_temperature = meter.temperature()

        zone = zones[sync_device['zone_id']]

        logger.info(f'{meter.device_name} reports a temperature of {meter_temperature} °C while tado returns {zone.temperature}')

        if abs(meter_temperature - zone.temperature) > 0.5:
            new_offset = meter_temperature - zone.temperature + zone.offset

            logger.info(f'Changing temperature offset to {new_offset:.02f} from {zone.offset:.02jf}')
            zone.offset = new_offset


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
