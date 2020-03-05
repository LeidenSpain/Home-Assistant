"""Support for retrieving meteorological data from Dark Sky."""

from datetime import datetime, timedelta, timezone
import logging

from requests.exceptions import (
    ConnectionError as ConnectError, HTTPError, Timeout)
import voluptuous as vol

from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION, ATTR_FORECAST_PRECIPITATION, ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TEMP_LOW, ATTR_FORECAST_TIME, ATTR_FORECAST_WIND_BEARING,
    ATTR_FORECAST_WIND_SPEED, PLATFORM_SCHEMA, WeatherEntity)
from homeassistant.components.darksky.weather import (DarkSkyWeather, DarkSkyData)
from homeassistant.const import (
    CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE, CONF_MODE, CONF_NAME,
    TEMP_CELSIUS, TEMP_FAHRENHEIT)
import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle

REQUIREMENTS = ['python-forecastio==1.4.0']

_LOGGER = logging.getLogger(__name__)

ATTRIBUTION = "Powered by Dark Sky mod"

FORECAST_MODE = ['hourly', 'daily']

CONF_UNITS = 'units'

ATTR_WEATHER_CLOUDS = 'cloud_cover'
ATTR_WEATHER_ALERTS = 'alerts'
ATTR_WEATHER_ALERT_CNT = 'alert_cnt'

DEFAULT_NAME = 'Dark Skym'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_KEY): cv.string,
    vol.Optional(CONF_LATITUDE): cv.latitude,
    vol.Optional(CONF_LONGITUDE): cv.longitude,
    vol.Optional(CONF_MODE, default='hourly'): vol.In(FORECAST_MODE),
    vol.Optional(CONF_UNITS): vol.In(['auto', 'si', 'us', 'ca', 'uk', 'uk2']),
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=5)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Dark Sky weather."""
    latitude = config.get(CONF_LATITUDE, hass.config.latitude)
    longitude = config.get(CONF_LONGITUDE, hass.config.longitude)
    name = config.get(CONF_NAME)
    mode = config.get(CONF_MODE)

    units = config.get(CONF_UNITS)
    if not units:
        units = 'ca' if hass.config.units.is_metric else 'us'

    dark_sky = DarkSkyDatam(
        config.get(CONF_API_KEY), latitude, longitude, units)

    add_entities([DarkSkyWeather_m(name, dark_sky, mode)], True)

class DarkSkyWeather_m(DarkSkyWeather):
    """Representation of a weather condition."""

    def __init__(self, *args):
        super().__init__(*args)
        self._ds_alert = None

    @property
    def state_attributes(self):
        clouds = self._ds_currently.get('cloudCover')
        data = super().state_attributes

        if clouds is not None:
            data[ATTR_WEATHER_CLOUDS] = round(clouds * 100, 1)

        if self._ds_alert:
            alerts = []
            for a in self._ds_alert():
                d = {
                        'title': a.json.get('title'),
                        'severity': a.json.get('severity'),
                        'time': datetime.fromtimestamp(a.json.get('time'), timezone.utc).astimezone().strftime('%d.%m.%Y %H:%M %Z'),
                        'expires': datetime.fromtimestamp(a.json.get('expires'), timezone.utc).astimezone().strftime('%d.%m.%Y %H:%M %Z'),
                        'description': a.json.get('description'),
                        'uri': a.json.get('uri')
                    }
                alerts.append(d)
            data[ATTR_WEATHER_ALERT_CNT] = len(alerts)

        if data[ATTR_WEATHER_ALERT_CNT]:
            data[ATTR_WEATHER_ALERTS] = alerts
        return data

    def update(self):
        super().update()
        self._ds_alert = self._dark_sky.alert

class DarkSkyDatam(DarkSkyData):
    """Get the latest data from Dark Sky."""

    def __init__(self, *args):
        """Initialize the data object."""

        super().__init__(*args)
        self.alert = None

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the latest data from Dark Sky."""

        super().update()
        if self.data is not None:
            self.alert = self.data.alerts
