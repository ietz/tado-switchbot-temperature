from typing import Optional

from PyTado.interface import Tado


class TadoZone:
    def __init__(self, tado: Tado, data):
        self._tado = tado
        self._data = data
        self.state = None

    @property
    def leader_id(self) -> str:
        for device in self._data['devices']:
            if 'ZONE_LEADER' in device['duties']:
                return device['serialNo']

    @property
    def temperature(self) -> Optional[float]:
        if self.state is None:
            return None

        return self.state['sensorDataPoints']['insideTemperature']['celsius']

    @property
    def offset(self) -> float:
        return self._tado.getDeviceInfo(self.leader_id, cmd='temperatureOffset')['celsius']

    @offset.setter
    def offset(self, value: float):
        self._tado.setTempOffset(self.leader_id, value)


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
