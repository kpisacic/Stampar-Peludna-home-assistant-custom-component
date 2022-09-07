# Stampar-Peludna-home-assistant-custom-component
Pollen alergy forecast ("Peludna prognoza") for Republic of Croatia, by Public Health Institute "Andrija Štampar"

The `stampar_pelud` sensor platform provide pollen forecast data for Republic of Croatia. Data is provided by
Public Health Institute "Andrija Štampar"  - https://stampar.hr/hr/peludna-prognoza .

Component uses web scraping technique for obtaining the data from the public web pages.

Sensor can be watched in Home Assistant with standard Entity and Entity Glance cards, or using custom build card for it https://github.com/kpisacic/lovelace-stampar-pelud-card .

The following device types and data are supported:

- [Sensor](#sensor) - Current conditions

## Installation

There are two options; manual or HACS installation:

*Manual installation*
- Copy `stamper_pelud`  folder in `custom_components` from repository to your Home Assistant configuration `custom_components` folder. Don't copy any other YAML files from repository root not to overwrite your own configuration.

*HACS installation*

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

- Use HACS custom repository (not default) - (https://github.com/kpisacic/Stampar-Peludna-home-assistant-custom-component)

## Location Selection

Platform can determine location in any of following ways:
- by reading configuration parameter `station_id` - see [station_id](#stationid) for list of currently supported station ID's
- by reading configuration parameter `longitude` and `latitude` of desired location, and then determining closest sensor
- by reading home assistant's location, and then determining closest measurement stop

So, minimum configuration is without any named configuration parameters other then platform name `stampar_pelud`.

When selecting location, you need to observe type of data reported by the service - some locations only report level of pollen per plant types (trees, grass), other locations beside level report most significant pollen plant, while some give also exact numeric value of level. Output of the sensor will be adjusted depending on available data from measurement.

## Sensor

The `stampar_pelud` sensor platform creates sensors based on Štampar's current conditions data and daily forecasts.

To add sensor to your installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
sensor:
  - platform: stampar_pelud
    name: Peludna prognoza
    station_id: 24
    latitude: 45.82123
    longitude: 16.05123
    allergens: [3,25,5,6]
```

- A sensor will be created for each of the liste plants being monitored by Štampar, see list of [plants](#plants). Default name like `sensor.<name>_<plant_name>`.

*Configuration*
- name:
  - description: Name to be used for the entity ID, e.g. `sensor.<name>_<plant_name>`.
  - required: false
  - default: "Peludna prognoza"
  - type: string
- station_id:
  - description: The station code of a specific station to use - see [stations](#stationid)
  - required: false
  - default: automatically determined, by HA location or separately provided longitute and latitude
  - type: string
- longitude:
  - description: Longitude of location to use for closest station determination
  - required: false
  - type: float
- latitude:
  - description: Latitude of location to use for closest station determination
  - required: false
  - type: float
- allergens:
  - description: List of plants to monitor, and create as sensors in home assistant. Since there are many plants, you can limit your monitored list to only those which are of interest to you
  - required: false
  - type: list of plant identifiers see list of [plants](#plants) - e.g. [3,4,5,6]

## station_id

    2   Beli Manastir 
    3   Bjelovar     
    4   Dubrovnik     
    5   Đakovo        
    6   Karlovac      
    7   Koprivnica    
    8   Kutina        
    9   Labin         
    10   Metković      
    11  Našice        
    12  Osijek        
    13  Pazin         
    14  Popovača      
    15  Poreč         
    16  Pula          
    17  Rijeka        
    18  Šibenik       
    19  Sisak         
    20  Slavonski Brod
    21  Split         
    22  Varaždin      
    23  Virovitica    
    24  Zadar         
    25  Zagreb        

## plants

    2    Lijeska     
    3    Joha        
    4    Čempresi    
    5    Jasen       
    6    Breza       
    7    Grab        
    8    Hrast       
    9    Platana     
    11   Koprive     
    12   Pitomi kesten
    13   Ambrozija   
    14   Pelin       
    15   Loboda      
    16   Maslina     
    17   Bor         
    18   Hrast crnika
    19   Crkvina     
    20   Vrba        
    21   Trputac     
    22   Topola      
    25   Brijest     
    26   Lipa        
    27   Orah        
    28   Kiselica    
    90   Drveće      
    10   Trave       
    92   Korovi      

