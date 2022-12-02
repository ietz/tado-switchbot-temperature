from typing import List, Dict

from switchbot_client import SwitchBotClient
from switchbot_client.devices import MeterPlus

from tado_switchbot_temperature.config import SyncDevice, settings


def get_meters(sync_devices: List[SyncDevice]) -> Dict[str, MeterPlus]:
    switchbot = get_switchbot_client()
    meter_ids = set(sync_device['meter_id'] for sync_device in sync_devices)
    devices = {meter_id: switchbot.device(meter_id) for meter_id in meter_ids}

    for device in devices.values():
        if not isinstance(device, MeterPlus):
            raise InvalidMeterError()

    return devices


class InvalidMeterError(Exception):
    pass


def print_available_meters():
    switchbot = get_switchbot_client()
    for device in switchbot.devices():
        if isinstance(device, MeterPlus):
            print(f'id = {device.device_id}, name = {device.device_name}')


def get_switchbot_client():
    return SwitchBotClient(token=settings['switchbot.open_token'], secret_key=settings['switchbot.secret_key'])
