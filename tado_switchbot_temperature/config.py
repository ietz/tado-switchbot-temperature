from typing import TypedDict

from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="TADO_SB",
    settings_files=['settings.toml', '.secrets.toml'],
)


class SyncDevice(TypedDict):
    zone_id: int
    meter_id: str
