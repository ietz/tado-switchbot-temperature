# tado-switchbot-temperature
[tado°](https://www.tado.com/) automates your heating based on a schedule, possibly augmented by open window detection and geofencing.
One major drawback of the system is that the [Smart Radiator Thermostats](https://www.tado.com/de-en/smart-radiator-thermostat) are bad at measuring the current temperature because of their proximity to the radiator.
The thermostats often report a temperature multiple degrees off from the temperature measured in the middle of the room.
To address this issue, tado° offers an add-on Wireless Temperature Sensor that works well but isn't exactly cheap at a listing price of 100€ per room.

This repository allows you to employ [SwitchBot meters](https://eu.switch-bot.com/pages/switchbot-meter-plus) with a similar effect as the tado° Wireless Temperature Sensors but at a more affordable ~20€ a piece.
It periodically compares the temperature measured by the SwitchBot meters to that reported by the tado° thermostats and updates your tado° settings, changing the thermostat's temperature offset.
In this, it uses the historical measurements to ensure that the temperatures match on average, rather than at a given instant.
This way, the offset won't change too often, as it could otherwise interfere with your heating and the smart features such as open window detection.
Your tado° system will still to its thing, just with a little course correction.

With the current implementation, you have to enable the SwitchBot cloud features for all meters which requires a SwitchBot hub.

## Usage
You will need your tado° account credentials and your SwitchBot open token and secret key.
The tado° credentials are the same you also use to login to the tado° app.
To obtain you SwitchBot open token and secret key, open the SwitchBot app, navigate to your profile
&rarr; preferences
&rarr; tap the app version 10 times
&rarr; open the now visible developer options
&rarr; press the _get token_ button.

### With Docker
1. Display an overview of all your tado° zones with
   ```shell
   docker run --rm \
         -e 'TADO_SB_SWITCHBOT__OPEN_TOKEN=myopentoken' \
         -e 'TADO_SB_SWITCHBOT__SECRET_KEY=mysecretkey' \
         ietz/tado-switchbot-temperature meters
   ```
   the output will look like
   ```
   id = 1, name = Living Room
   id = 2, name = Kitchen
   id = 5, name = Bedroom
   id = 6, name = Bathroom
   ```
   
2. Display an overview of all your SwitchBot meters with
   ```shell
   docker run --rm \
         -e 'TADO_SB_TADO__USERNAME=me@example.com' \
         -e 'TADO_SB_TADO__PASSWORD=mypassword' \
         ietz/tado-switchbot-temperature meters
   ```
   the output will look like
   ```
   id = C1234A5678B9, name = Living Room Meter
   id = C35F1958D1AA, name = Bedroom Meter
   id = FB5C15796242, name = Kitchen Meter
   ```
3. Create a `docker-compose.yml` using the environment variables to configure the module as described in the config section
   ```yaml
   version: "3.8"
   
   services:
       tado_switchbot:
           build: .
           environment:
               TADO_SB_TADO__USERNAME: "me@example.com"
               TADO_SB_TADO__PASSWORD: "mypassword"
               TADO_SB_SWITCHBOT__OPEN_TOKEN: "myopentoken"
               TADO_SB_SWITCHBOT__SECRET_KEY: "mysecretkey"
               TADO_SB_DEVICES: >
                   [
                       { zone_id = 1, meter_id = 'C1234A5678B9' },
                       { zone_id = 2, meter_id = 'C35F1958D1AA' },
                       { zone_id = 5, meter_id = 'FB5C15796242' }
                   ]
               TADO_SB_LOGGING__LEVEL: "INFO"
   ```

### Without Docker
1. Clone the repository
2. Set your tado° and SwitchBot authentication data as shown in the _Configuration: Secrets_ section below
3. Run `python -m tado_switchbot_temperature zones` to see an overview of all your tado° zones
   ```
   id = 1, name = Living Room
   id = 2, name = Kitchen
   id = 5, name = Bedroom
   id = 6, name = Bathroom
   ```
4. Run `python -m tado_switchbot_temperature meters` to see an overview of all your SwitchBot meters
   ```
   id = C1234A5678B9, name = Living Room Meter
   id = C35F1958D1AA, name = Bedroom Meter
   id = FB5C15796242, name = Kitchen Meter
   ```
5. Set the `devices` configuration as shown in the _Configuration: Settings_ and all the other settings you want to adjust
6. Run `python -m tado_switchbot_temperature sync`

## Configuration
You can configure the module with a `settings.toml`, a `.secrets.toml`, using environment variables, or an arbitrary combination of the three.
The TOML-Content below gives an overview of all available configuration properties alongside a short explanation.

For environment variables, prefix the configuration key with `TADO_SB_` followed by the configuration key.
If the configuration key is inside a TOML table, like the `username` inside the `[tado]` table, use a double (!) underscore `__` to separate the table name from the key.

For example, you can set your tado° username either
- in the `.secrets.toml` inside the `[tado]` table with the `username` key, as shown below, or
- in the `settings.toml`, also inside the `[tado]` table with the `username` key, or
- as an environment variable `TADO_SB_TADO__PASSWORD=me@example.com`. Note the double underscore between `TADO` and `PASSWORD`.

These same three options apply to all configuration keys.


### Credentials
Intended for a `.secrets.toml` or environment variables, but can also be a part of the `settings.toml`.

```toml
[tado]
# Tado account data
username = "me@example.com"
password = "mypassword"

[switchbot]
# The authentication for switchbot
open_token = "myopentoken"
secret_key = "mysecretkey"
```

### Settings
Intended for the `settings.toml` or environment variables.
Only the `devices` key is required, all others use a sensible default.

```toml
# How often to compare the temperatures reported by the thermostats to the meters (interval in seconds)
probe_interval = 300

# The minimum temperature difference required to update the offset (in degrees celsius)
# For example: With an offset_update_threshold of 0.2, the module will update the thermostat's offset only when the
# temperature is at least 0.2 off from the meter's temperature. It won't change the offset in the tado° settings if the
# thermostat reports 20.5 °C while the meter reports 20.6°, but it will if the meter reports at least 20.7° or less than
# 20.3°.
offset_update_threshold = 0.5

# Controls how much the offset should be based on the current measurement vs. historical measurements.
# With lower values, the module will place higher importance on the most recent measurements. 
# If set to 0, it will only ever compare the latest thermostat measurement to the latest meter measurement, ignoring all
# previous measurements.
# With a higher value, it will instead consider a larger time window when comparing the measurements.
# More concretely, this value specifies the half-life in seconds of data point importance in the sense of exponential
# moving averages.
offset_smoothing_halftime = 2700

# Which meters to sync with which tado zones.
# See the section on IDs below on how to find these values for your system
devices = [
    { zone_id = 1, meter_id = "C1234A5678B9" },  # e.g. living room
    { zone_id = 2, meter_id = "C35F1958D1AA" },  # e.g. kitchen
    { zone_id = 5, meter_id = "FB5C15796242" },  # e.g. bedroom
]

[logging]
# One of: CRITICAL, FATAL, ERROR, WARNING, INFO, DEBUG
level = "INFO"
# Where to write the logs in addition to the console
file = "sync.log"
```
