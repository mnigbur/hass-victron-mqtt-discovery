# Home Assistant MQTT discovery for Victron GX

[Victron GX MQTT](https://github.com/victronenergy/dbus-flashmq) integration that maps MQTT topics to [modbus registers](https://www.victronenergy.com/support-and-downloads/technical-information) and
uses this information to add [Home Assistant MQTT discovery](https://www.home-assistant.io/integrations/mqtt/#mqtt-discovery).

## Usage

This project comes packaged as a docker container. Running this container will watch for GX devices publishing on the MQTT broker and automatically generate entities for the discovered GX entities.

Options can be provided as environment variables.

Only the `MQTT_HOST` environment variable is required, it should be set to the MQTT broker on which topics will be published.
If you do not run a separate MQTT broker `MQTT_HOST` should be set to the IP of your Victron GX.

```sh
docker run --name hass-victron-mqtt-discovery -ti --restart=always -e MQTT_HOST=192.168.1.10
```

| Variable | Default | Description | Required |
| --- | --- | --- | --- |
| `MQTT_HOST` | | The address of the MQTT server to subscribe and publish to | Yes |
| `MQTT_PORT` | `1883` | The port on which the MQTT server runs | No |
| `MQTT_PREFIX` | `""` | The prefix to subscribe to. If you Victron data is published using a prefix, specify it here | No |
| `ASSET_MODBUS_REGISTERS_URL` | [link](https://www.victronenergy.com/upload/documents/CCGX-Modbus-TCP-register-list-3.50.xlsx) | The URL to the Victron provided list of modbus registers | No |
| `ASSET_SENSOR_DOCUMENTATION_URL` | [link](https://developers.home-assistant.io/docs/core/entity/sensor/) | The URL to the Home Assistant Sensor Entity documentation | No |

## Disclaimer

This project enables interaction with your Victron GX device using MQTT, based on official Victron documentation. It does not alter or modify the GX device software itself.

- This code is provided as is.
- The developer does not assume any liability for issues caused by the use of this integration.
- Use at your own risk.
