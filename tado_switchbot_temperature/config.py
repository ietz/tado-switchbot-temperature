from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="TADO_SB",
    settings_files=['settings.toml', '.secrets.toml'],
)
