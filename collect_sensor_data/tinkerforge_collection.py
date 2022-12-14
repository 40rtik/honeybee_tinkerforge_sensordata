from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_thermal_imaging import BrickletThermalImaging
from tinkerforge.bricklet_sound_pressure_level import BrickletSoundPressureLevel
from tinkerforge.bricklet_humidity_v2 import BrickletHumidityV2
from tinkerforge.bricklet_outdoor_weather import BrickletOutdoorWeather
from tinkerforge.bricklet_temperature_ir_v2 import BrickletTemperatureIRV2
from tinkerforge.bricklet_co2_v2 import BrickletCO2V2

import os
import time
import math
from PIL import Image
import json
from datetime import datetime

HOST = "localhost"
PORT = 4223

#
current_time = datetime.now()
image_path = 'data' + str(os.sep) + 'thermal_image_' + str(current_time)
data_path = 'data' + str(os.sep) + 'sensor_data_' + str(current_time)


# Creates standard thermal image color palette (blue=cold, red=hot)
def get_thermal_image_color_palette():
    palette = []

    for x in range(256):
        x /= 255.0
        palette.append(int(round(255*math.sqrt(x))))                  # RED
        palette.append(int(round(255*pow(x, 3))))                     # GREEN
        if math.sin(2 * math.pi * x) >= 0:
            palette.append(int(round(255*math.sin(2 * math.pi * x)))) # BLUE
        else:
            palette.append(0)

    return palette

def thermal_imaging_bricklet(ipcon):
    UID = "Hkw1" # Change XYZ to the UID of your Thermal Imaging Bricklet
    SCALE = 10 # Use scale 10 for 800x600 size
    
    ti = BrickletThermalImaging(UID, ipcon) # Create device object

    ipcon.connect(HOST, PORT) # Connect to brickd
    # Don't use device before ipcon is connected

    # Enable high contrast image transfer for getter
    ti.set_image_transfer_config(ti.IMAGE_TRANSFER_MANUAL_HIGH_CONTRAST_IMAGE)

    ti.set_resolution(ti.RESOLUTION_0_TO_655_KELVIN)
    ti.set_spotmeter_config(['0','0','79','59'])

    # If we change between transfer modes we have to wait until one more
    # image is taken after the mode is set and the first image is saved 
    # we can call get_high_contrast_image any time.
    time.sleep(0.5)

    # Get image data
    image_data = ti.get_high_contrast_image()
    
    # Make PNG with PIL
    image = Image.new('P', (80, 60))
    image.putdata(image_data)

    # This puts a color palette into place, if you 
    # remove this line you will get a greyscale image.
    image.putpalette(get_thermal_image_color_palette())

    # Scale to 800x600 and save thermal image!
    image.resize((80*SCALE, 60*SCALE), Image.ANTIALIAS).save(image_path + '.png')
    
    thermal_image_dict = dict()
    thermal_image_dict['thermal_image'] = image_data
    thermal_image_dict['thermal_image_statistics'] = ti.get_statistics()
    
    return thermal_image_dict

def sound_pressure_level_bricklet(ipcon):
    UID = 'FNi' 
    ti = BrickletSoundPressureLevel(UID, ipcon)
    # 128: 64 Gruppen, 80 Samples pro Sekunde, jede Gruppe hat Größe 320Hz
    # dB(Z) besitzt keine Gewichtung und gibt die Daten ungewichtet zurück
    ti.set_configuration(ti.FFT_SIZE_128, ti.WEIGHTING_Z)
    sound_pressure_dict = dict()
    sound_pressure_dict['decibel'] = ti.get_decibel()
    sound_pressure_dict['spectrum'] = ti.get_spectrum()
    
    return sound_pressure_dict

def humidity_bricklet_V2(ipcon):
    UID = 'H9g'
    ti = BrickletHumidityV2(UID, ipcon)
    humidity_dict = dict()
    humidity_dict['humidity']=ti.get_humidity()
    humidity_dict['temperature']=ti.get_temperature()
    return humidity_dict

def outdoor_weather_bricklet(ipcon):
    UID = 'ErL'
    ti = BrickletOutdoorWeather(UID, ipcon)
    outdoor_weather_dict = dict()
    outdoor_weather_dict['sensor_data'] = ti.get_sensor_data(ti.get_sensor_identifiers()[0])
    outdoor_weather_dict['station_data'] = ti.get_station_data(ti.get_station_identifiers()[0])
    return outdoor_weather_dict

def temperature_ir_bricklet_V2(ipcon):
    UID = 'Env'
    ti = BrickletTemperatureIRV2(UID, ipcon)
    temperature_ir_dict = dict()
    temperature_ir_dict['ambient_temperature'] = ti.get_ambient_temperature()
    temperature_ir_dict['object_temperature'] = ti.get_object_temperature()
    return temperature_ir_dict

def co2_V2_bricklet(ipcon):
    UID = 'Jwo'
    ti = BrickletCO2V2(UID, ipcon)
    co2_concentration, temperature, humidity = ti.get_all_values()
    co2_V2_dict = dict()
    co2_V2_dict['co2_concentration'] =co2_concentration
    co2_V2_dict['temperature'] = temperature
    co2_V2_dict['humidity'] = humidity
    return co2_V2_dict
    
if __name__ == "__main__":
    ipcon = IPConnection() # Create IP connection
    #collect thermal_image_data
    data_collection = dict()
    data_collection['thermal_imaging_bricklet'] = thermal_imaging_bricklet(ipcon)
    data_collection['sound_pressure_bricklet'] = sound_pressure_level_bricklet(ipcon)
    data_collection['humidity_bricklet_V2'] = humidity_bricklet_V2(ipcon)
    data_collection['outdoor_weather_bricklet_V2'] = outdoor_weather_bricklet(ipcon)
    data_collection['temperature_ir_bricklet_V2'] = temperature_ir_bricklet_V2(ipcon)
    data_collection['co2_V2_bricklet'] = co2_V2_bricklet(ipcon)
    
    ipcon.disconnect()
    
    with open(data_path+'.json', 'w') as fp:
        json.dump(data_collection, fp)