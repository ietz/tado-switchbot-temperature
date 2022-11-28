import logging
from typing import List, Dict

from switchbot_client import SwitchBotClient
from switchbot_client.devices import MeterPlusUs, MeterPlusJp

from tado_switchbot_temperature.config import settings, SyncDevice

logger = logging.getLogger(__name__)


def sync():
    logger.info(f'Tado username is {settings["tado.username"]} and password is {settings["tado.password"]}')

    sync_devices: List[SyncDevice] = settings['devices']
    meters = get_meters(sync_devices)
    for meter in meters.values():
        logger.info(f'{meter.device_name} reports a temperature of {meter.temperature()} °C')


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
