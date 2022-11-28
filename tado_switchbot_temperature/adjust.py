from tado_switchbot_temperature.config import settings


def adjust():
    print(f'Tado username is {settings["username"]} and password is {settings["password"]}')
