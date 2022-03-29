"""Sensor for the Štamper Peludna Prognoza."""
from datetime import timedelta, datetime, date
import logging
import voluptuous as vol
import requests
import lxml
from bs4 import BeautifulSoup

from homeassistant.const import (
    CONF_NAME,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    __version__,
)
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import SensorEntity
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

CONF_ALLERGENS = "allergens"
ATTR_NAME = "name"
ATTR_DATE = "date"
ATTR_LEVEL = "level"
ATTR_STATION = "station"
ATTR_UPDATED = "updated"
ATTR_DESCRIPTION = "description"
ATTR_IMAGE = "image"
ATTR_FORECAST = "forecast"
ATTRIBUTION = "Data provided by stampar.hr"
DEFAULT_NAME = "Peludna prognoza"
CONF_STATION_ID = "station_id"

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=60)

SENSOR_TYPES = {
    2 : { "name": "Lijeska"       , "name_clean": "lijeska"       , "lat": "Corylus sp."    , "type": "Drveće", "icon": "mdi:flower-pollen"  },
    3 : { "name": "Joha"          , "name_clean": "joha"          , "lat": "Alnus sp."      , "type": "Drveće", "icon": "mdi:flower-pollen"  },
    4 : { "name": "Čempresi"      , "name_clean": "cempresi"      , "lat": "Cupressaceae"   , "type": "Drveće", "icon": "mdi:flower-pollen"  },
    5 : { "name": "Jasen"         , "name_clean": "jasen"         , "lat": "Fraxinus sp."   , "type": "Drveće", "icon": "mdi:flower-pollen"  },
    6 : { "name": "Breza"         , "name_clean": "breza"         , "lat": "Betula sp."     , "type": "Drveće", "icon": "mdi:flower-pollen"  },
    7 : { "name": "Grab"          , "name_clean": "grab"          , "lat": "Carpinus sp."   , "type": "Drveće", "icon": "mdi:flower-pollen"  },
    8 : { "name": "Hrast"         , "name_clean": "hrast"         , "lat": "Quercus sp."    , "type": "Drveće", "icon": "mdi:flower-pollen"  },
    9 : { "name": "Platana"       , "name_clean": "platana"       , "lat": "Platanus sp."   , "type": "Drveće", "icon": "mdi:flower-pollen"  },
    11: { "name": "Koprive"       , "name_clean": "koprive"       , "lat": "Urticaceae"     , "type": "Korovi", "icon": "mdi:flower-pollen"  },
    12: { "name": "Pitomi kesten" , "name_clean": "pitomi_kesten" , "lat": "Castanea sativa", "type": "Drveće", "icon": "mdi:flower-pollen"  },
    13: { "name": "Ambrozija"     , "name_clean": "ambrozija"     , "lat": "Ambrosia sp."   , "type": "Korovi", "icon": "mdi:flower-pollen"  },
    14: { "name": "Pelin"         , "name_clean": "pelin"         , "lat": "Artemisia sp."  , "type": "Korovi", "icon": "mdi:flower-pollen"  },
    15: { "name": "Loboda"        , "name_clean": "loboda"        , "lat": "Chenopodiaceae" , "type": "Korovi", "icon": "mdi:flower-pollen"  },
    16: { "name": "Maslina"       , "name_clean": "maslina"       , "lat": "Olea sp."       , "type": "Drveće", "icon": "mdi:flower-pollen"  },
    17: { "name": "Bor"           , "name_clean": "bor"           , "lat": "Pinus sp."      , "type": "Drveće", "icon": "mdi:flower-pollen"  },
    18: { "name": "Hrast crnika"  , "name_clean": "hrast_crnika"  , "lat": "Quercus ilex"   , "type": "Drveće", "icon": "mdi:flower-pollen"  },
    19: { "name": "Crkvina"       , "name_clean": "crkvina"       , "lat": "Parietaria sp." , "type": "Korovi", "icon": "mdi:flower-pollen"  },
    20: { "name": "Vrba"          , "name_clean": "vrba"          , "lat": "Salix sp."      , "type": "Drveće", "icon": "mdi:flower-pollen"  },
    21: { "name": "Trputac"       , "name_clean": "trputac"       , "lat": "Plantago sp."   , "type": "Korovi", "icon": "mdi:flower-pollen"  },
    22: { "name": "Topola"        , "name_clean": "topola"        , "lat": "Populus sp."    , "type": "Drveće", "icon": "mdi:flower-pollen"  },
    25: { "name": "Brijest"       , "name_clean": "brijest"       , "lat": "Ulmus sp."      , "type": "Drveće", "icon": "mdi:flower-pollen"  },
    26: { "name": "Lipa"          , "name_clean": "lipa"          , "lat": "Tilia sp."      , "type": "Drveće", "icon": "mdi:flower-pollen"  },
    27: { "name": "Orah"          , "name_clean": "orah"          , "lat": "Juglans sp."    , "type": "Drveće", "icon": "mdi:flower-pollen"  },
    28: { "name": "Kiselica"      , "name_clean": "kiselica"      , "lat": "Rumex sp."      , "type": "Korovi", "icon": "mdi:flower-pollen"  },
    90: { "name": "Drveće"        , "name_clean": "drvece"        , "lat": "Drveće"         , "type": "Drveće", "icon": "mdi:flower-pollen"  },
    10: { "name": "Trave"         , "name_clean": "trave"         , "lat": "Poaceae"        , "type": "Trave" , "icon": "mdi:flower-pollen"  },
    92: { "name": "Korovi"        , "name_clean": "korovi"        , "lat": "Korovi"         , "type": "Korovi", "icon": "mdi:flower-pollen"  },
}

STATIONS = {
    "2" : { "name":"Beli Manastir"  , "lat": 45.7729, "long": 18.6108 },
    "3" : { "name":"Dubrovnik"      , "lat": 42.6507, "long": 18.0944 },
    "4" : { "name":"Đakovo"         , "lat": 45.3100, "long": 18.4098 },
    "5" : { "name":"Karlovac"       , "lat": 45.4929, "long": 15.5553 },
    "6" : { "name":"Koprivnica"     , "lat": 46.1639, "long": 16.8335 },
    "7" : { "name":"Kutina"         , "lat": 45.4793, "long": 16.7763 },
    "8" : { "name":"Labin"          , "lat": 45.0916, "long": 14.1238 },
    "9" : { "name":"Metković"       , "lat": 43.0533, "long": 17.6493 },
    "10": { "name":"Našice"         , "lat": 45.4947, "long": 18.0951 },
    "11": { "name":"Osijek"         , "lat": 45.5550, "long": 18.6955 },
    "12": { "name":"Pazin"          , "lat": 45.2398, "long": 13.9373 },
    "13": { "name":"Popovača"       , "lat": 45.5713, "long": 16.6274 },
    "14": { "name":"Poreč"          , "lat": 45.2272, "long": 13.5947 },
    "15": { "name":"Pula"           , "lat": 44.8666, "long": 13.8496 },
    "16": { "name":"Rijeka"         , "lat": 45.3271, "long": 14.4422 },
    "17": { "name":"Šibenik"        , "lat": 43.7350, "long": 15.8952 },
    "18": { "name":"Sisak"          , "lat": 45.4851, "long": 16.3731 },
    "19": { "name":"Slavonski Brod" , "lat": 45.1631, "long": 18.0116 },
    "20": { "name":"Split"          , "lat": 43.5147, "long": 16.4435 },
    "21": { "name":"Varaždin"       , "lat": 46.3057, "long": 16.3366 },
    "22": { "name":"Virovitica"     , "lat": 45.8316, "long": 17.3855 },
    "23": { "name":"Zadar"          , "lat": 44.1194, "long": 15.2314 },
    "24": { "name":"Zagreb"         , "lat": 45.8150, "long": 15.9819 },
}

LEVELS = {
    "0": { "from": 0 , "to": 0 , "medium": "0" , "title": "nema peludi" , "title_eng": "none"       , "color": "gray"   },
    "1": { "from": 0 , "to": 2 , "medium": "1" , "title": "niska"       , "title_eng": "low"        , "color": "green"  },
    "2": { "from": 2 , "to": 6 , "medium": "4" , "title": "umjerena"    , "title_eng": "medium"     , "color": "yellow" },
    "3": { "from": 6 , "to": 12, "medium": "9" , "title": "visoka"      , "title_eng": "high"       , "color": "orange" },
    "4": { "from": 12, "to": 99, "medium": "15", "title": "jako visoka" , "title_eng": "veryhigh"   , "color": "red"    },
}

PLATFORM_SCHEMA = cv.PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_ALLERGENS, default=list(SENSOR_TYPES) ): vol.All(
            cv.ensure_list, [vol.In(SENSOR_TYPES)]
        ),        
        vol.Optional(CONF_STATION_ID): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Inclusive(
            CONF_LATITUDE, "coordinates", "Latitude and longitude must exist together"
        ): cv.latitude,
        vol.Inclusive(
            CONF_LONGITUDE, "coordinates", "Latitude and longitude must exist together"
        ): cv.longitude,
    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Štampar Pelud sensor platform."""
    name = config.get(CONF_NAME)
    station_id = config.get(CONF_STATION_ID)
    latitude = config.get(CONF_LATITUDE, hass.config.latitude)
    longitude = config.get(CONF_LONGITUDE, hass.config.longitude)

    station_id = config.get(CONF_STATION_ID) 
    if station_id:
        _LOGGER.debug("Configuration station_id: %s", station_id)
        if station_id not in STATIONS:
            _LOGGER.error("Configuration %s: %s , is not known", CONF_STATION_ID, station_id)
            return False            
    else:
        station_id = closest_station(latitude, longitude)
        _LOGGER.debug("Found closest station_id: %s", station_id)

    station_name = STATIONS[station_id]["name"]
    _LOGGER.debug("Determined station name: %s", station_name)

    probe = StamparPeludData(station_id=station_id, station_name=station_name)
    try:
        probe.update()
    except (ValueError, TypeError) as err:
        _LOGGER.error("Received error from stampar.hr: %s", err)
        return False

    add_entities(
        [
            StamparPeludSensor(probe, variable, name, station_id, station_name)
            for variable in config[CONF_ALLERGENS]
        ],
        True,
    )


class StamparPeludSensor(SensorEntity):
    """Implementation of a Štampar Pelud sensor."""

    def __init__(self, probe, variable, name, station_id, station_name):
        """Initialize the sensor."""
        self.probe = probe
        self.client_name = name
        self.variable = variable
        self.station_id = station_id
        self.station_name = station_name
        _LOGGER.debug("Initializing: %s", variable)

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.client_name} {SENSOR_TYPES[self.variable]['name_clean']}"

    @property
    def icon(self):
        """Return the name of the sensor."""
        return SENSOR_TYPES[self.variable]["icon"]

    @property
    def state(self):
        """Return the state of the sensor."""
        ret = None
        l_data = self.probe.get_data(SENSOR_TYPES[self.variable]["name"])
        #_LOGGER.debug("Found mapped data: %s", l_data)
        if l_data:
            if len(l_data["measurements"]) > 0:
                first_measurement =  l_data["measurements"][0]
                if first_measurement:
                    if first_measurement["value"] != "":
                        ret = float(first_measurement["value"])
                    else:
                        ret = first_measurement["level"]
        return ret

    @property
    def state_class(self):
        """Return the state_class of this entity, if any."""
        return "measurement"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        ret = {
            ATTR_NAME: SENSOR_TYPES[self.variable]["name"],
            ATTR_STATION: self.probe.get_location(),
            ATTR_UPDATED: self.probe._last_update,
        }
        l_data = self.probe.get_data(SENSOR_TYPES[self.variable]["name"])
        if l_data:
            if len(l_data["measurements"]) > 0:
                level_measurement = None
                date_measurement = None
                level_measurement_en = None
                forecast = {}
                first_measurement =  l_data["measurements"][0]
                if first_measurement:
                    level_measurement = first_measurement["level"]
                    date_measurement = first_measurement["date"]
                    for measurement in l_data["measurements"][1:]:
                        forecast[measurement["date"]] = measurement["level"]
                ret = {
                    ATTR_NAME: SENSOR_TYPES[self.variable]["name"],
                    ATTR_LEVEL: level_measurement,
                    ATTR_DATE: date_measurement,
                    ATTR_STATION: self.probe.get_location(),
                    ATTR_UPDATED: self.probe._last_update,
                    ATTR_DESCRIPTION: l_data.get("description"),
                    ATTR_IMAGE: l_data.get("image"),
                    ATTR_FORECAST: forecast,
                }
        return ret

    @property
    def entity_picture(self):
        ret = None
        l_data = self.probe.get_data(SENSOR_TYPES[self.variable]["name"])
        if l_data:
            ret = l_data.get("small_image")
        # ret = "/local/stampar_icons/" + SENSOR_TYPES[self.variable]["name"] + ".svg"
        return ret

    def update(self):
        """Delegate update to probe."""
        self.probe.update()

class StamparPeludData:
    """The class for handling the data retrieval."""

    _station_name = ""
    _station_id = ""
    _data = {}
    _last_update = None

    def __init__(self, station_id, station_name):
        """Initialize the probe."""
        self._station_name = station_name
        self._station_id = station_id
        self._data = {}
        _LOGGER.debug("Initialized sensor data: %s, %s", station_id, station_name)

    def current_situation(self):
        """Fetch and parse the latest XML data."""
        try:
            # Return structure with received parsed data
            # title                 - station title as received from API
            # min_date              - minimum date of measurements
            # max_first_date        - maximum first measurement date
            # plants: {
            #   plant_key: {         - HR name  of plant, from API
            #     title             - name fo plant, from API
            #     small_image       - small image URL
            #     image             - big image URL
            #     description       - long plant description
            #     measurements: [
            #       date            - date in noted format (first date is measurement, others are forecasts)
            #       level           - levels: nema peludi, niska, umjerena, visoka, jako visoka
            #       value           - measured value, or medium is only level given
            #     ]
            #   }
            # }
            elem = {
                "title": "",
                "min_date": None,
                "max_first_date": None,
                "plants": {},
            }

            _LOGGER.debug("Refreshing current_situation")

            l_headers = {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "User-Agent": "Mozilla/5.0",
                "Origin": "https://stampar.hr",
                "Referer": "https://stampar.hr/hr/peludna-prognoza"
            }

            l_data = {
                "title": self._station_id,
                "view_name": "peludna_prognoza",
                "view_display_id": "block_1",
            }

            r = requests.post("https://stampar.hr/hr/views/ajax?_wrapper_format=drupal_ajax", headers=l_headers, data=l_data)
            l_response = r.json()

            for i_response in l_response:
                if "data" in i_response:
                    if "view-peludna-prognoza" in i_response["data"]:
                        l_data = i_response["data"]
            
            #_LOGGER.debug("Received data response: %s", l_data)

            s = BeautifulSoup(l_data, "lxml")

            l_title = ""
            if s.find("div", class_="views-field-title"):
                l_title = s.find("div", class_="views-field-title").get_text("", strip=True)

            _LOGGER.debug("Response title: %s", l_title)
            elem["title"] = l_title

            for plant in s.find_all("div", class_="paragraph--type--biljka-grupa"):

                plant_title = plant.find("div", class_="biljka-naslov").get_text("", strip=True)
                plant_key = plant_title.partition("(")[0].strip()
                _LOGGER.debug("Found plant: %s, key: %s", plant_title, plant_key)
                plant_big_img = ""
                plant_small_img = ""
                plant_desc = ""
                if plant.img:
                    plant_big_img = "https://stampar.hr" + plant.img['src']
                s_plant_desc = plant.find("div", class_="opis-biljke")
                if s_plant_desc:
                    if s_plant_desc.img:
                        plant_small_img = "https://stampar.hr" + s_plant_desc.img["src"]
                    s_plant_desc_text = s_plant_desc.find("div", class_="field-type-text-with-summary")
                    if s_plant_desc_text:
                        plant_desc = s_plant_desc_text.get_text("", strip=True)

                _LOGGER.debug("Plant small image: %s, image: %s, and descritpion: %s", plant_small_img, plant_big_img, plant_desc)

                d_measurements = []

                d_first_measurement = None

                for measurement in plant.find_all("div", class_="mjerenje-container"):
                
                    date_measurement = measurement.find("div", class_="field-field-datum-mjerenja").find("div", class_="field-item").get_text("", strip=True)
                    _LOGGER.debug("Found measurement of date: %s", date_measurement)
                    d_date_measurement = datetime.strptime(date_measurement, '%d.%m.%Y.').date()

                    ## logic excluded, let sensor store all fetched data, filtering of only future dates should be done in frontend
                    # if d_date_measurement < date.today():
                    #     _LOGGER.debug("Found measurement date is in past, ignoring it: %s < %s", d_date_measurement , date.today())
                    # else:

                    level_measurement = ""
                    s_level_measurement = measurement.find("div", class_="field-field-vrijednost-tekst")
                    if s_level_measurement:
                        level_measurement = s_level_measurement.find("div", class_="field-item").get_text("", strip=True)
                    value_measurement = ""
                    s_value = measurement.find("div", class_="field-field-vrijednost")
                    if s_value:
                        value_measurement = s_value.find("div", class_="field-item").get_text("", strip=True)

                    _LOGGER.debug("Original level: %s and value: %s", level_measurement, value_measurement)

                    if level_measurement == "" and value_measurement != "" and not value_measurement.replace(".","").isdigit():
                        level_measurement = value_measurement
                        value_measurement = ""

                    _LOGGER.debug("Aligned level: %s and value: %s", level_measurement, value_measurement)

                    d_measurements.append( {
                        "date": date_measurement,
                        "level": level_measurement,
                        "value": value_measurement
                    } )
                    
                    if not d_first_measurement:
                        d_first_measurement = d_date_measurement
                        if not elem["max_first_date"] or d_first_measurement > elem["max_first_date"]:
                            elem["max_first_date"] = d_first_measurement

                    if not elem["min_date"] or d_date_measurement < elem["min_date"]:
                        elem["min_date"] = d_date_measurement

                elem["plants"][plant_key] = {
                    "title": plant_title,
                    "small_image": plant_small_img,
                    "image": plant_big_img,
                    "description": plant_desc,
                    "measurements": d_measurements
                }

                s_major = plant.find("div", class_="prevladava-container")
                if s_major:
                    for major in s_major.find_all("article"):
                        major_plant = major.find("span").get_text("", strip=True)
                        major_plant_key = major_plant.partition("(")[0].strip()

                        _LOGGER.debug("Found major plant: %s, key: %s", major_plant, major_plant_key)

                        s_plant_desc_text = major.find("div", class_="field-type-text-with-summary")
                        if s_plant_desc_text:
                            major_plant_desc = s_plant_desc_text.get_text("", strip=True)
                        if major.find("img"):
                            major_plant_small_img = "https://stampar.hr" + major.img["src"]
                        
                        _LOGGER.debug("Major plant image: %s, and description: %s", major_plant_small_img, major_plant_desc)

                        elem["plants"][major_plant_key] = {
                            "title": major_plant,
                            "small_image": major_plant_small_img,
                            "image": "",
                            "description": major_plant_desc,
                            "measurements": d_measurements
                        }

            return elem

        except requests.ConnectionError as err:
            _LOGGER.error("Requests Connection error: %s", err.strerror )
        except requests.HTTPError as err:
            _LOGGER.error("Requests HTTP error: %s", err.strerror )
        except requests.Timeout as err:
            _LOGGER.error("Requests Timeout error: %s", err.strerror )
        except requests.RequestException as err:
            _LOGGER.error("Requests exception: %s", err.strerror )


    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the latest data from Štampar Peludna."""

        if self._last_update and ( self._last_update + timedelta(hours=1) > datetime.now() ):
            _LOGGER.debug("Skipping sensor data update, last_update was: %s", self._last_update)
            return

        ## logic excluded, seems like data can be updated more then once per day
        # if self._data.get("min_date") and self._data.get("min_date") >= date.today():
        #     _LOGGER.debug("Skipping sensor data update, already have data for today: %s >= %s", self._data.get("min_date"), date.today() )
        #     return

        _LOGGER.debug("Doing sensor data update, last_update was: %s", self._last_update)

        s_current_data = self.current_situation()
        if s_current_data:
            self._data = s_current_data

        _LOGGER.debug("Sensor, current data: %s", self._data)

        self._last_update = datetime.now()
        _LOGGER.debug("Setting last_update to: %s", self._last_update)

        _LOGGER.debug("Updating - finished.")

    def get_data(self, variable):
        """Get the data."""
        return self._data["plants"].get(variable)

    def get_location(self):
        """Get the location title."""
        return self._data["title"]

def closest_station(lat, lon):
    """Return the ID of the closest station to our lat/lon."""
    _LOGGER.debug("Closest station, lat: %s, lon: %s", lat, lon)
    if lat is None or lon is None:
        return

    def comparable_dist(stat_id):
        """Calculate the pseudo-distance from lat/lon."""
        station_lon = STATIONS[stat_id]["long"]
        station_lat = STATIONS[stat_id]["lat"]
        return (lat - station_lat) ** 2 + (lon - station_lon) ** 2

    return min(STATIONS, key=comparable_dist)
