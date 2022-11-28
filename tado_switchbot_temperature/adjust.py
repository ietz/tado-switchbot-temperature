from typing import List

from switchbot_client import SwitchBotClient
from switchbot_client.devices import MeterPlusUs, MeterPlusJp

from tado_switchbot_temperature.config import settings, SyncDevice


def adjust():
    print(f'Tado username is {settings["tado.username"]} and password is {settings["tado.password"]}')

    switchbot = SwitchBotClient(token=settings['switchbot.open_token'])

    sync_devices: List[SyncDevice] = settings['devices']

    for sync_device in sync_devices:
        print(sync_device)
        meter = switchbot.device(sync_device['meter_id'])
        if not isinstance(meter, (MeterPlusUs, MeterPlusJp)):
            raise InvalidMeterError()

        print(f'{meter.device_name} reports a temperature of {meter.temperature()} °C')


class InvalidMeterError(Exception):
    pass
