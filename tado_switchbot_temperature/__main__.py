from tado_switchbot_temperature.adjust import adjust
from tado_switchbot_temperature.config import settings
from tado_switchbot_temperature.logging import configure_logging

configure_logging(log_file_name=settings.get('log_file', None))
adjust()
