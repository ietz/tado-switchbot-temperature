import datetime as dt
from typing import Optional

from PyTado.interface import Tado


class TadoZone:
    def __init__(self, tado: Tado, data):
        self._tado = tado
        self._data = data
        self.state = None
        self._offset: Optional[float] = None
        self._offset_update_timestamp: Optional[dt.datetime] = None

    @property
    def leader_id(self) -> str:
        for device in self._data['devices']:
            if 'ZONE_LEADER' in device['duties']:
                return device['serialNo']

    @property
    def temperature(self) -> Optional[float]:
        """The current temperature. Is None if not updated since the last offset change"""
        if self.state is None:
            return None

        temperature_measurement = self.state['sensorDataPoints']['insideTemperature']
        measurement_timestamp = dt.datetime.fromisoformat(temperature_measurement['timestamp'].replace('Z', '+00:00'))
        if measurement_timestamp < self._offset_update_timestamp:
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
        self._offset_update_timestamp = dt.datetime.now()
        self._offset = value


class TadoZones:
    def __init__(self, tado: Tado):
        self._tado = tado
        self._zones = {zone_data['id']: TadoZone(tado=tado, data=zone_data) for zone_data in tado.getZones()}

    def __getitem__(self, item) -> TadoZone:
        return self._zones[item]

    def update(self):
        zone_states = self._tado.getZoneStates()['zoneStates']
        for zone_id, zone_state in zone_states:
            self[zone_id].state = zone_state
