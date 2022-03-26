# Stampar-Peludna-home-assistant-custom-component
Pollen alergy forecast ("Peludna prognoza") for Republic of Croatia, by Public Health Institute "Andrija Štampar"

The `stampar_pelud` sensor platform provide pollen forecast data for Republic of Croatia. Data is provided by
Public Health Institute "Andrija Štampar"  - https://stampar.hr/hr/peludna-prognoza .
Custom pollen forecast card is also included in the package.

The following device types and data are supported:

- [Sensor](#sensor) - Current conditions
- [Custom Card](#custom-card) - Custom lovelace card with semaphore indicators

## Installation

There are two options; manual or HACS installation:

*Manual installation*
- Copy `stamper_pelud`  folder in `custom_components` from repository to your Home Assistant configuration `custom_components` folder. Don't copy any other YAML files from repository root not to overwrite your own configuration.
- Copy `stamper-pelud-card.js` from `www` repository folder to your Home Assistant configuration `www` folder
- Copy folder `stampar_icons` with all files from `www` repository folder to your Home Assistant configuration `www` folder

*HACS installation*

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

- Use HACS custom repository (not default) - (https://github.com/kpisacic/Stampar-Peludna-home-assistant-custom-component)
- Copy `dhmz-weather-card.js` from `www` repocitory folder to your Home Assistant configuration `www` folder
- Copy folder `stampar_icons` with all files from `www` repository folder to your Home Assistant configuration `www` folder

## Location Selection

Platform can determine location in any of following ways:
- by reading configuration parameter `station_id` - see [station_id](#stationid) for list of currently supported station ID's
- by reading configuration parameter `longitude` and `latitude` of desired location, and then determining closest sensor
- by reading home assistant's location, and then determining closest measurement stop

So, minimum configuration is without any named configuration parameters other then platform name `stampar_pelud`.

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
  - type: list of plant identifiers see list of [plants](#plants)

## station_id

    2   Beli Manastir 
    3   Dubrovnik     
    4   Đakovo        
    5   Karlovac      
    6   Koprivnica    
    7   Kutina        
    8   Labin         
    9   Metković      
    10  Našice        
    11  Osijek        
    12  Pazin         
    13  Popovača      
    14  Poreč         
    15  Pula          
    16  Rijeka        
    17  Šibenik       
    18  Sisak         
    19  Slavonski Brod
    20  Split         
    21  Varaždin      
    22  Virovitica    
    23  Zadar         
    24  Zagreb        

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

## Custom card

To add custom card for Štampar pollen forecast, add following to your lovelace configuration YAML file:

1. Under resources section add custom card definition 

```yaml
resources:
  - type: js
    url: /local/stampar-pelud-card.js
```


2. In views and cards section add following card

```yaml
    cards:
      - type: 'custom:stampar-pelud-card'
        sensor: Peludna prognoza
        allergens: [3,25,5,6]
        icons: simple
```

- `sensor` - mandatory attribute, you should state name of the entity configured in sensor compontent
- `allergens` - optional attribute, you can specify which plants to display, if left empty display all plants from sensor
- `icons` - optional which icons to use, options are: simple, stampar, png1, png2, jpg, photo
