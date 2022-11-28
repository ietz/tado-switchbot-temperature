from typing import TypedDict

from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="TADO_SB",
    settings_files=['settings.toml', '.secrets.toml'],
)


class SyncDevice(TypedDict):
    meter_id: str
    valve_id: str
