import datetime as dt
from typing import Optional, Iterable

from PyTado.interface import Tado

from tado_switchbot_temperature.config import settings


class TadoZone:
    def __init__(self, tado: Tado, data):
        self._tado = tado
        self._data = data
        self.state = None
        self._offset: Optional[float] = None
        self._offset_update_timestamp: Optional[dt.datetime] = None

    @property
    def id(self) -> int:
        return self._data['id']

    @property
    def leader_id(self) -> str:
        for device in self._data['devices']:
            if 'ZONE_LEADER' in device['duties']:
                return device['serialNo']

    @property
    def name(self) -> str:
        return self._data['name']

    @property
    def temperature(self) -> Optional[float]:
        """The current temperature. Is None if not updated since the last offset change"""
        if self.state is None:
            return None

        temperature_measurement = self.state['sensorDataPoints']['insideTemperature']
        measurement_timestamp = dt.datetime.fromisoformat(temperature_measurement['timestamp'].replace('Z', '+00:00'))
        if self._offset_update_timestamp is not None and measurement_timestamp < self._offset_update_timestamp:
            return None

        return temperature_measurement['celsius']

    @property
    def offset(self) -> float:
        if self._offset is None:
            self._offset = self._tado.getDeviceInfo(self.leader_id, cmd='temperatureOffset')['celsius']

        return self._offset

    @offset.setter
    def offset(self, value: float):
        self._tado.setTempOffset(self.leader_id, value)
        self._offset_update_timestamp = dt.datetime.now().astimezone()
        self._offset = value


class TadoZones:
    def __init__(self, tado: Tado):
        self._tado = tado
        self._zones = {zone_data['id']: TadoZone(tado=tado, data=zone_data) for zone_data in tado.getZones()}

    @staticmethod
    def from_config() -> 'TadoZones':
        return TadoZones(Tado(username=settings['tado.username'], password=settings['tado.password']))

    def __iter__(self) -> Iterable[TadoZone]:
        return iter(self._zones.values())

    def __getitem__(self, item) -> TadoZone:
        return self._zones[item]

    def update(self):
        zone_states = self._tado.getZoneStates()['zoneStates']
        for zone_id, zone_state in zone_states.items():
            self[int(zone_id)].state = zone_state


def print_available_zones():
    for zone in TadoZones.from_config():
        print(f'id = {zone.id}, name = {zone.name}')
