from flask import Flask, jsonify, render_template, session
from flask_wtf import FlaskForm
from wtforms import Form, SubmitField, TextField
import os
import glob
import json
import re
import time
from scipy.interpolate import interp1d
from datetime import datetime, timedelta

'''
Konfigurationsparameter für den Webserver, sowie die Pfadstruktur an der die Jsons gesucht werden.
Der Pfad hat die Form: /example/dataset  unter dem Verzeichnis dataset befinden sich Verzeichnise für jeweils einen Tag, mit JSONs für diesen Tag.
Somit wird aus dem Pfad durch die Applikation die Form /example/dataset/2020-06-20/*json erstellt.
'''
root_path_to_jsons = '/home/user/example/dataset'
delta = 60*24

server_port = 5000
server_ip = 'localhost'
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = os.urandom(32)

class Navigationform(FlaskForm):
    start = SubmitField('start')
    nextday = SubmitField('next day')
    daybefore = SubmitField('day before')
    end = SubmitField('end')
    all = SubmitField('all')
    datum = TextField('date')

def findAllRecordedData(path, index, full_data_set=False):
    '''
    Ermittelt auf basis der übergebenen Parameter eine aufgezeichneten Datensatz der Tinkerforge-Sensoren.
    :param path:
    :param index:
    :param full_data_set:
    :return:
    '''

    indexlist = sorted([d.split('sensor_data/')[1] for d in glob.glob(path + '/20*')])
    date = ''
    if index < 0:
        index = 0
        date = indexlist[0]
    elif index > len(indexlist) - 1:
        index = len(indexlist)-1
        date = indexlist[index]
    else:
        date = indexlist[index]
    d = indexlist[index]
    if full_data_set:
        # date = indexlist[0]
        date = '*'
        d = '*'

    jsonFileList = []
    jsonFileList.extend(glob.glob(path + '/' + d + '/*.json'))

    print(' search date: ' + str(index) + ' ---------------')

    jsonFileList.sort()
    # jeden x-ten Messwert in den Response übernehmen, da sonst zuviele Werte ausgelesen werden müssen und dies dauert
    # zu lange beim Laden durch den Browser
    if not full_data_set:
        # jsonFileList = jsonFileList[0::20]
        jsonFileList = jsonFileList
    else:
        # jsonFileList = jsonFileList[0::100]
        jsonFileList = jsonFileList
    print('Anzahl gefundener Jsons: ' + str(len(jsonFileList)))

    fileList = list()

    outdoor_weather_bricklet_V2_station_data_temperature = list()
    outdoor_weather_bricklet_V2_station_data_humidity = list()
    outdoor_weather_bricklet_V2_sensor_data_temperature = list()
    outdoor_weather_bricklet_V2_sensor_data_humidity = list()
    outdoor_weather_bricklet_V2_sensor_data_rain = list()
    temperature_ir_bricklet_v2_ambient_temperature = list()
    temperature_ir_bricklet_v2_object_temperature = list()
    co2_V2_bricklet_co2_concentration = list()
    co2_V2_bricklet_co2_temperature = list()
    co2_V2_bricklet_co2_humidity = list()
    humidity_bricklet_V2_humidity = list()
    humidity_bricklet_V2_temperature = list()
    sound_pressure_bricklet_decibel = list()
    thermal_imaging_bricklet_average_temperature = list()
    thermal_imaging_bricklet_max_temperature = list()
    thermal_imaging_bricklet_min_temperature = list()

    initial_data = None
    if len(jsonFileList)>0:
        with open(jsonFileList[0]) as init_file:
            d = json.load(init_file)
            initial_data = d['outdoor_weather_bricklet_V2']['station_data'][4] / 10.0

    for jsonPath in jsonFileList:
        try:
            with open(jsonPath) as json_file:
                data = json.load(json_file)

                thermal_imaging_bricklet = data['thermal_imaging_bricklet']
                thermal_image_statistics = thermal_imaging_bricklet['thermal_image_statistics']
                thermal_image_bricklet_average_temperature = (thermal_image_statistics[0][0] / 100.0) - 273.15
                thermal_imaging_bricklet_average_temperature.append(thermal_image_bricklet_average_temperature)
                thermal_image_bricklet_max_temperature = (thermal_image_statistics[0][1] / 100.0) - 273.15
                thermal_imaging_bricklet_max_temperature.append(thermal_image_bricklet_max_temperature)
                thermal_image_bricklet_min_temperature = (thermal_image_statistics[0][2] / 100.0) - 273.15
                thermal_imaging_bricklet_min_temperature.append(thermal_image_bricklet_min_temperature)

                outdoor_weather_bricklet_V2 = data['outdoor_weather_bricklet_V2']
                outdoor_weather_bricklet_V2_station_data_temperature.append(outdoor_weather_bricklet_V2['station_data'][0] / 10.0)
                outdoor_weather_bricklet_V2_station_data_humidity.append(outdoor_weather_bricklet_V2['station_data'][1])
                outdoor_weather_bricklet_V2_sensor_data_temperature.append(outdoor_weather_bricklet_V2['sensor_data'][0] / 10.0)
                outdoor_weather_bricklet_V2_sensor_data_humidity.append(outdoor_weather_bricklet_V2['sensor_data'][1])
                if initial_data:
                    outdoor_weather_bricklet_V2_sensor_data_rain.append((outdoor_weather_bricklet_V2['station_data'][4] / 10.0) - initial_data)
                else:
                    outdoor_weather_bricklet_V2_sensor_data_rain.append(
                        outdoor_weather_bricklet_V2['station_data'][4] / 10.0)

                co2_V2_bricklet = data['co2_V2_bricklet']
                co2_V2_bricklet_co2_concentration.append(co2_V2_bricklet['co2_concentration'])
                co2_V2_bricklet_co2_temperature.append(co2_V2_bricklet['temperature'] / 100.0)
                co2_V2_bricklet_co2_humidity.append(co2_V2_bricklet['humidity'] / 100.0 )

                humidity_bricklet_V2 = data['humidity_bricklet_V2']
                humidity_bricklet_V2_temperature.append(humidity_bricklet_V2['temperature'] / 100.0)
                humidity_bricklet_V2_humidity.append(humidity_bricklet_V2['humidity'] / 100.0)

                sound_brick = data['sound_pressure_bricklet']
                # sound_pressure_bricklet_decibel.append(sound_brick['decibel'] / 10.0)
                sound_pressure_bricklet_decibel.append((sum(sound_brick['spectrum']) / len(sound_brick['spectrum']))*1000)

                temperature_ir_bricklet_v2_ambient_temperature.append(data['temperature_ir_bricklet_V2']['ambient_temperature'] / 10.0 )
                temperature_ir_bricklet_v2_object_temperature.append(data['temperature_ir_bricklet_V2']['object_temperature'] / 10.0 )

                fileList.append(re.search('[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}',jsonPath.split('sensor_data_')[1]).group(0))
        except Exception as e:
            print('Error in file: ' + jsonPath)

    print('Anzahl gefundener Datensätze: ' + str(len(fileList)))
    return outdoor_weather_bricklet_V2_station_data_temperature, \
           outdoor_weather_bricklet_V2_station_data_humidity, \
           outdoor_weather_bricklet_V2_sensor_data_rain, \
           outdoor_weather_bricklet_V2_sensor_data_temperature, \
           outdoor_weather_bricklet_V2_sensor_data_humidity, \
           co2_V2_bricklet_co2_concentration, \
           co2_V2_bricklet_co2_temperature, \
           co2_V2_bricklet_co2_humidity, \
           humidity_bricklet_V2_temperature, \
           humidity_bricklet_V2_humidity, \
           sound_pressure_bricklet_decibel, \
           temperature_ir_bricklet_v2_ambient_temperature, \
           temperature_ir_bricklet_v2_object_temperature, \
           thermal_imaging_bricklet_average_temperature, \
           thermal_imaging_bricklet_max_temperature, \
           thermal_imaging_bricklet_min_temperature, \
           fileList, date, index, len(indexlist), indexlist


def createLinearFunction(outdoor_weather_bricklet_V2_station_data_temperature, \
            outdoor_weather_bricklet_V2_station_data_humidity, \
            outdoor_weather_bricklet_V2_sensor_data_rain, \
            outdoor_weather_bricklet_V2_sensor_data_temperature, \
            outdoor_weather_bricklet_V2_sensor_data_humidity, \
            co2_V2_bricklet_co2_concentration, \
            co2_V2_bricklet_co2_temperature, \
            co2_V2_bricklet_co2_humidity, \
            humidity_bricklet_V2_temperature, \
            humidity_bricklet_V2_humidity, \
            sound_pressure_bricklet_decibel, \
            temperature_ir_bricklet_v2_ambient_temperature, \
            temperature_ir_bricklet_v2_object_temperature, \
            thermal_imaging_bricklet_average_temperature, \
            thermal_imaging_bricklet_max_temperature, \
            thermal_imaging_bricklet_min_temperature, \
            fileList, full_data_selection):
    fileList_ = [time.strptime(c_time, '%Y-%m-%d %H:%M:%S') for c_time in fileList]
    fileList = [time.mktime(c_time) - time.mktime(fileList_[0]) for c_time in fileList_]

    # create linear function
    fc_outdoor_weather_bricklet_V2_station_data_temperature = interp1d(fileList,
                                                                       outdoor_weather_bricklet_V2_station_data_temperature,
                                                                       kind='linear', axis=- 1,
                                                                       copy=True, bounds_error=None,
                                                                       assume_sorted=False)
    fc_outdoor_weather_bricklet_V2_station_data_humidity = interp1d(fileList,
                                                                    outdoor_weather_bricklet_V2_station_data_humidity,
                                                                    kind='linear', axis=- 1,
                                                                    copy=True, bounds_error=None,
                                                                    assume_sorted=False)
    fc_outdoor_weather_bricklet_V2_sensor_data_rain = interp1d(fileList,
                                                                    outdoor_weather_bricklet_V2_sensor_data_rain,
                                                                    kind='linear', axis=- 1,
                                                                    copy=True, bounds_error=None,
                                                                    assume_sorted=False)
    fc_outdoor_weather_bricklet_V2_sensor_data_temperature = interp1d(fileList,
                                                                      outdoor_weather_bricklet_V2_sensor_data_temperature,
                                                                      kind='linear', axis=- 1,
                                                                      copy=True, bounds_error=None,
                                                                      assume_sorted=False)
    fc_outdoor_weather_bricklet_V2_sensor_data_humidity = interp1d(fileList,
                                                                   outdoor_weather_bricklet_V2_sensor_data_humidity,
                                                                   kind='linear', axis=- 1,
                                                                   copy=True, bounds_error=None,
                                                                   assume_sorted=False)
    fc_co2_V2_bricklet_co2_concentration = interp1d(fileList,
                                                    co2_V2_bricklet_co2_concentration,
                                                    kind='linear', axis=- 1,
                                                    copy=True, bounds_error=None,
                                                    assume_sorted=False)
    fc_co2_V2_bricklet_co2_temperature = interp1d(fileList,
                                                  co2_V2_bricklet_co2_temperature,
                                                  kind='linear', axis=- 1,
                                                  copy=True, bounds_error=None,
                                                  assume_sorted=False)
    fc_co2_V2_bricklet_co2_humidity = interp1d(fileList,
                                               co2_V2_bricklet_co2_humidity,
                                               kind='linear', axis=- 1,
                                               copy=True, bounds_error=None,
                                               assume_sorted=False)
    fc_humidity_bricklet_V2_temperature = interp1d(fileList,
                                                   humidity_bricklet_V2_temperature,
                                                   kind='linear', axis=- 1,
                                                   copy=True, bounds_error=None,
                                                   assume_sorted=False)
    fc_humidity_bricklet_V2_humidity = interp1d(fileList,
                                                humidity_bricklet_V2_humidity,
                                                kind='linear', axis=- 1,
                                                copy=True, bounds_error=None,
                                                assume_sorted=False)
    fc_sound_pressure_bricklet_decibel = interp1d(fileList,
                                                  sound_pressure_bricklet_decibel,
                                                  kind='linear', axis=- 1,
                                                  copy=True, bounds_error=None,
                                                  assume_sorted=False)
    fc_temperature_ir_bricklet_v2_ambient_temperature = interp1d(fileList,
                                                                 temperature_ir_bricklet_v2_ambient_temperature,
                                                                 kind='linear', axis=- 1,
                                                                 copy=True, bounds_error=None,
                                                                 assume_sorted=False)
    fc_temperature_ir_bricklet_v2_object_temperature = interp1d(fileList,
                                                                temperature_ir_bricklet_v2_object_temperature,
                                                                kind='linear', axis=- 1,
                                                                copy=True, bounds_error=None,
                                                                assume_sorted=False)
    fc_thermal_imaging_bricklet_average_temperature = interp1d(fileList,
                                                               thermal_imaging_bricklet_average_temperature,
                                                               kind='linear', axis=- 1,
                                                               copy=True, bounds_error=None,
                                                               assume_sorted=False)
    fc_thermal_imaging_bricklet_max_temperature = interp1d(fileList,
                                                           thermal_imaging_bricklet_max_temperature,
                                                           kind='linear', axis=- 1,
                                                           copy=True, bounds_error=None,
                                                           assume_sorted=False)
    fc_thermal_imaging_bricklet_min_temperature = interp1d(fileList,
                                                           thermal_imaging_bricklet_min_temperature,
                                                           kind='linear', axis=- 1,
                                                           copy=True, bounds_error=None,
                                                           assume_sorted=False)

    refraktometer_file = json.load(open("refraktometer.json"))
    ref_index = [refraktometer_file['refraktometer'].index(r)*12*60*60 for r in refraktometer_file['refraktometer']]
    ref_water_content = [r['water_content'] for r in refraktometer_file['refraktometer']]

    fc_refraktometer = interp1d(ref_index, ref_water_content, kind='linear', axis=- 1,
                                                           copy=True, bounds_error=None,
                                                           assume_sorted=False)
    ref_time = [time.strptime(c_time+'.2020', '%d.%m.%Y') for c_time in [r['date'] for r in refraktometer_file['refraktometer']]]
    sample_ref = []
    refraktometer_water_content = []
    for v in range(0, int(ref_index[-1]), 60):
        t = (datetime(*ref_time[0][:6]) + timedelta(seconds=v)).strftime('%d-%m %H:%M')
        sample_ref.append(t)
        refraktometer_water_content.append(fc_refraktometer(v))

    sample_def = []
    outdoor_weather_bricklet_V2_station_data_temperature = []
    outdoor_weather_bricklet_V2_station_data_humidity = []
    outdoor_weather_bricklet_V2_sensor_data_rain = []
    outdoor_weather_bricklet_V2_sensor_data_temperature = []
    outdoor_weather_bricklet_V2_sensor_data_humidity = []
    co2_V2_bricklet_co2_concentration = []
    co2_V2_bricklet_co2_temperature = []
    co2_V2_bricklet_co2_humidity = []
    humidity_bricklet_V2_temperature = []
    humidity_bricklet_V2_humidity = []
    sound_pressure_bricklet_decibel = []
    temperature_ir_bricklet_v2_ambient_temperature = []
    temperature_ir_bricklet_v2_object_temperature = []
    thermal_imaging_bricklet_average_temperature = []
    thermal_imaging_bricklet_max_temperature = []
    thermal_imaging_bricklet_min_temperature = []
    for v in range(0, int(fileList[-1]), 60):
        t = (datetime(*fileList_[0][:6]) + timedelta(seconds=v)).strftime('%d-%m %H:%M')
        sample_def.append(t)
        try:
            outdoor_weather_bricklet_V2_station_data_temperature.append(
                fc_outdoor_weather_bricklet_V2_station_data_temperature(v))
            outdoor_weather_bricklet_V2_station_data_humidity.append(
                fc_outdoor_weather_bricklet_V2_station_data_humidity(v))
            outdoor_weather_bricklet_V2_sensor_data_rain.append(
                fc_outdoor_weather_bricklet_V2_sensor_data_rain(v))
            outdoor_weather_bricklet_V2_sensor_data_temperature.append(
                fc_outdoor_weather_bricklet_V2_sensor_data_temperature(v))
            outdoor_weather_bricklet_V2_sensor_data_humidity.append(
                fc_outdoor_weather_bricklet_V2_sensor_data_humidity(v))
            co2_V2_bricklet_co2_concentration.append(fc_co2_V2_bricklet_co2_concentration(v))
            co2_V2_bricklet_co2_temperature.append(fc_co2_V2_bricklet_co2_temperature(v))
            co2_V2_bricklet_co2_humidity.append(fc_co2_V2_bricklet_co2_humidity(v))
            humidity_bricklet_V2_temperature.append(fc_humidity_bricklet_V2_temperature(v))
            humidity_bricklet_V2_humidity.append(fc_humidity_bricklet_V2_humidity(v))
            sound_pressure_bricklet_decibel.append(fc_sound_pressure_bricklet_decibel(v))
            temperature_ir_bricklet_v2_ambient_temperature.append(fc_temperature_ir_bricklet_v2_ambient_temperature(v))
            temperature_ir_bricklet_v2_object_temperature.append(fc_temperature_ir_bricklet_v2_object_temperature(v))
            thermal_imaging_bricklet_average_temperature.append(fc_thermal_imaging_bricklet_average_temperature(v))
            thermal_imaging_bricklet_max_temperature.append(fc_thermal_imaging_bricklet_max_temperature(v))
            thermal_imaging_bricklet_min_temperature.append(fc_thermal_imaging_bricklet_min_temperature(v))

            if len(sample_ref)<len(sample_def):
                sample_ref.append(t)
                refraktometer_water_content.append(0)

        except Exception as e:
            print(e)
    fileList = sample_def

    global delta
    delta_ = delta
    if not full_data_selection:
        delta_ = int(delta / 24)
    owbsdt_betrag_erst_ab = []
    for i, t in enumerate(outdoor_weather_bricklet_V2_station_data_temperature):
        if i < len(outdoor_weather_bricklet_V2_station_data_temperature) - 2 * delta_:
            x = sum(outdoor_weather_bricklet_V2_station_data_temperature[i + delta_:i + 2 * delta_])
            y = sum(outdoor_weather_bricklet_V2_station_data_temperature[i:i + delta_])
            res = (x - y) / delta_
            owbsdt_betrag_erst_ab.append(res)

    owbsdt_betrag_zweit_ab = []
    for i, t in enumerate(owbsdt_betrag_erst_ab):
        if i < len(owbsdt_betrag_erst_ab) - 2 * delta_:
            x = sum(owbsdt_betrag_erst_ab[i + delta_:i + 2 * delta_])
            y = sum(owbsdt_betrag_erst_ab[i:i + delta_])
            res = (x - y) / delta_
            owbsdt_betrag_zweit_ab.append(abs(res))

    if len(owbsdt_betrag_zweit_ab) != len(outdoor_weather_bricklet_V2_station_data_temperature):
        owbsdt_betrag_zweit_ab = owbsdt_betrag_zweit_ab[:len(outdoor_weather_bricklet_V2_station_data_temperature)] + [
            0] * (len(outdoor_weather_bricklet_V2_station_data_temperature) - len(owbsdt_betrag_zweit_ab))

    tmp = list(zip(owbsdt_betrag_zweit_ab, outdoor_weather_bricklet_V2_station_data_temperature,
                   outdoor_weather_bricklet_V2_station_data_humidity,
                   outdoor_weather_bricklet_V2_sensor_data_rain,
                   outdoor_weather_bricklet_V2_sensor_data_temperature,
                   outdoor_weather_bricklet_V2_sensor_data_humidity,
                   temperature_ir_bricklet_v2_ambient_temperature,
                   temperature_ir_bricklet_v2_object_temperature,
                   co2_V2_bricklet_co2_concentration,
                   co2_V2_bricklet_co2_temperature,
                   co2_V2_bricklet_co2_humidity,
                   humidity_bricklet_V2_humidity,
                   humidity_bricklet_V2_temperature,
                   sound_pressure_bricklet_decibel,
                   thermal_imaging_bricklet_average_temperature,
                   thermal_imaging_bricklet_max_temperature,
                   thermal_imaging_bricklet_min_temperature,
                   sample_ref, refraktometer_water_content, fileList))
    return tmp


@app.route('/', methods=['GET', 'POST'])
def chart():
    outdoor_weather_bricklet_V2_station_data_temperature = []
    outdoor_weather_bricklet_V2_station_data_humidity = []
    outdoor_weather_bricklet_V2_sensor_data_temperature = []
    outdoor_weather_bricklet_V2_sensor_data_humidity = []
    co2_V2_bricklet_co2_concentration = []
    co2_V2_bricklet_co2_temperature = []
    co2_V2_bricklet_co2_humidity = []
    humidity_bricklet_V2_temperature = []
    humidity_bricklet_V2_humidity = []
    sound_pressure_bricklet_decibel = []
    temperature_ir_bricklet_v2_ambient_temperature = []
    temperature_ir_bricklet_v2_object_temperature = []
    thermal_imaging_bricklet_average_temperature = []
    thermal_imaging_bricklet_max_temperature = []
    thermal_imaging_bricklet_min_temperature = []
    fileList = []
    index_count = 0
    date_list = []

    nav_form = Navigationform()

    index = 0
    full_data_selection=False
    if nav_form.all.data:
        outdoor_weather_bricklet_V2_station_data_temperature, \
        outdoor_weather_bricklet_V2_station_data_humidity, \
        outdoor_weather_bricklet_V2_sensor_data_rain, \
        outdoor_weather_bricklet_V2_sensor_data_temperature, \
        outdoor_weather_bricklet_V2_sensor_data_humidity, \
        co2_V2_bricklet_co2_concentration, \
        co2_V2_bricklet_co2_temperature, \
        co2_V2_bricklet_co2_humidity, \
        humidity_bricklet_V2_temperature, \
        humidity_bricklet_V2_humidity, \
        sound_pressure_bricklet_decibel, \
        temperature_ir_bricklet_v2_ambient_temperature, \
        temperature_ir_bricklet_v2_object_temperature, \
        thermal_imaging_bricklet_average_temperature, \
        thermal_imaging_bricklet_max_temperature, \
        thermal_imaging_bricklet_min_temperature, \
        fileList, date, index, index_count, date_list = findAllRecordedData(root_path_to_jsons, index, full_data_set=True)
        full_data_selection = True

        session['index'] = index
    else:
        if 'index' in session:
            index = session['index']

            outdoor_weather_bricklet_V2_station_data_temperature, \
            outdoor_weather_bricklet_V2_station_data_humidity, \
            outdoor_weather_bricklet_V2_sensor_data_rain, \
            outdoor_weather_bricklet_V2_sensor_data_temperature, \
            outdoor_weather_bricklet_V2_sensor_data_humidity, \
            co2_V2_bricklet_co2_concentration, \
            co2_V2_bricklet_co2_temperature, \
            co2_V2_bricklet_co2_humidity, \
            humidity_bricklet_V2_temperature, \
            humidity_bricklet_V2_humidity, \
            sound_pressure_bricklet_decibel, \
            temperature_ir_bricklet_v2_ambient_temperature, \
            temperature_ir_bricklet_v2_object_temperature, \
            thermal_imaging_bricklet_average_temperature, \
            thermal_imaging_bricklet_max_temperature, \
            thermal_imaging_bricklet_min_temperature, \
            fileList, date, index, index_count, date_list = findAllRecordedData(root_path_to_jsons, index)

            session['index'] = index
        else:
            outdoor_weather_bricklet_V2_station_data_temperature, \
            outdoor_weather_bricklet_V2_station_data_humidity, \
            outdoor_weather_bricklet_V2_sensor_data_rain, \
            outdoor_weather_bricklet_V2_sensor_data_temperature, \
            outdoor_weather_bricklet_V2_sensor_data_humidity, \
            co2_V2_bricklet_co2_concentration, \
            co2_V2_bricklet_co2_temperature, \
            co2_V2_bricklet_co2_humidity, \
            humidity_bricklet_V2_temperature, \
            humidity_bricklet_V2_humidity, \
            sound_pressure_bricklet_decibel, \
            temperature_ir_bricklet_v2_ambient_temperature, \
            temperature_ir_bricklet_v2_object_temperature, \
            thermal_imaging_bricklet_average_temperature, \
            thermal_imaging_bricklet_max_temperature, \
            thermal_imaging_bricklet_min_temperature, \
            fileList, date, index, index_count, date_list = findAllRecordedData(root_path_to_jsons, index)

            session['index'] = index

        if nav_form.nextday.data:
            print('nextday')
            index += 1
            session['index'] = index

            outdoor_weather_bricklet_V2_station_data_temperature, \
            outdoor_weather_bricklet_V2_station_data_humidity, \
            outdoor_weather_bricklet_V2_sensor_data_rain, \
            outdoor_weather_bricklet_V2_sensor_data_temperature, \
            outdoor_weather_bricklet_V2_sensor_data_humidity, \
            co2_V2_bricklet_co2_concentration, \
            co2_V2_bricklet_co2_temperature, \
            co2_V2_bricklet_co2_humidity, \
            humidity_bricklet_V2_temperature, \
            humidity_bricklet_V2_humidity, \
            sound_pressure_bricklet_decibel, \
            temperature_ir_bricklet_v2_ambient_temperature, \
            temperature_ir_bricklet_v2_object_temperature, \
            thermal_imaging_bricklet_average_temperature, \
            thermal_imaging_bricklet_max_temperature, \
            thermal_imaging_bricklet_min_temperature, \
            fileList, date, index, index_count, date_list = findAllRecordedData(root_path_to_jsons, index)
        if nav_form.daybefore.data:
            print('daybefore')
            index -= 1
            session['index'] = index

            outdoor_weather_bricklet_V2_station_data_temperature, \
            outdoor_weather_bricklet_V2_station_data_humidity, \
            outdoor_weather_bricklet_V2_sensor_data_rain, \
            outdoor_weather_bricklet_V2_sensor_data_temperature, \
            outdoor_weather_bricklet_V2_sensor_data_humidity, \
            co2_V2_bricklet_co2_concentration, \
            co2_V2_bricklet_co2_temperature, \
            co2_V2_bricklet_co2_humidity, \
            humidity_bricklet_V2_temperature, \
            humidity_bricklet_V2_humidity, \
            sound_pressure_bricklet_decibel, \
            temperature_ir_bricklet_v2_ambient_temperature, \
            temperature_ir_bricklet_v2_object_temperature, \
            thermal_imaging_bricklet_average_temperature, \
            thermal_imaging_bricklet_max_temperature, \
            thermal_imaging_bricklet_min_temperature, \
            fileList, date, index, index_count, date_list = findAllRecordedData(root_path_to_jsons, index)

        if nav_form.start.data:
            print('start')
            index = 0
            session['index'] = index

            outdoor_weather_bricklet_V2_station_data_temperature, \
            outdoor_weather_bricklet_V2_station_data_humidity, \
            outdoor_weather_bricklet_V2_sensor_data_rain, \
            outdoor_weather_bricklet_V2_sensor_data_temperature, \
            outdoor_weather_bricklet_V2_sensor_data_humidity, \
            co2_V2_bricklet_co2_concentration, \
            co2_V2_bricklet_co2_temperature, \
            co2_V2_bricklet_co2_humidity, \
            humidity_bricklet_V2_temperature, \
            humidity_bricklet_V2_humidity, \
            sound_pressure_bricklet_decibel, \
            temperature_ir_bricklet_v2_ambient_temperature, \
            temperature_ir_bricklet_v2_object_temperature, \
            thermal_imaging_bricklet_average_temperature, \
            thermal_imaging_bricklet_max_temperature, \
            thermal_imaging_bricklet_min_temperature, \
            fileList, date, index, index_count, date_list = findAllRecordedData(root_path_to_jsons, index)

        if nav_form.end.data:
            print('end')
            index = 1000
            session['index'] = index

            outdoor_weather_bricklet_V2_station_data_temperature, \
            outdoor_weather_bricklet_V2_station_data_humidity, \
            outdoor_weather_bricklet_V2_sensor_data_rain, \
            outdoor_weather_bricklet_V2_sensor_data_temperature, \
            outdoor_weather_bricklet_V2_sensor_data_humidity, \
            co2_V2_bricklet_co2_concentration, \
            co2_V2_bricklet_co2_temperature, \
            co2_V2_bricklet_co2_humidity, \
            humidity_bricklet_V2_temperature, \
            humidity_bricklet_V2_humidity, \
            sound_pressure_bricklet_decibel, \
            temperature_ir_bricklet_v2_ambient_temperature, \
            temperature_ir_bricklet_v2_object_temperature, \
            thermal_imaging_bricklet_average_temperature, \
            thermal_imaging_bricklet_max_temperature, \
            thermal_imaging_bricklet_min_temperature, \
            fileList, date, index, index_count, date_list = findAllRecordedData(root_path_to_jsons, index)

    nav_form.datum = date

    # create linear interpolations to get sections with a length of one minute
    tmp = createLinearFunction(outdoor_weather_bricklet_V2_station_data_temperature, \
            outdoor_weather_bricklet_V2_station_data_humidity, \
            outdoor_weather_bricklet_V2_sensor_data_rain, \
            outdoor_weather_bricklet_V2_sensor_data_temperature, \
            outdoor_weather_bricklet_V2_sensor_data_humidity, \
            co2_V2_bricklet_co2_concentration, \
            co2_V2_bricklet_co2_temperature, \
            co2_V2_bricklet_co2_humidity, \
            humidity_bricklet_V2_temperature, \
            humidity_bricklet_V2_humidity, \
            sound_pressure_bricklet_decibel, \
            temperature_ir_bricklet_v2_ambient_temperature, \
            temperature_ir_bricklet_v2_object_temperature, \
            thermal_imaging_bricklet_average_temperature, \
            thermal_imaging_bricklet_max_temperature, \
            thermal_imaging_bricklet_min_temperature, \
            fileList, full_data_selection)

    max_elements = 24/2
    if full_data_selection:
        max_elements = index_count
        # tmp = tmp[0::100]
    # else:
    #     tmp = tmp[0::20]
    tmp = [[*x] for x in zip(*tmp)]

    return render_template('time_charts.html', max_elements=max_elements,
                           day_scaling='true' if full_data_selection else 'false',
                           legend0='outdoor_weather_bricklet_V2_station_data_temperature_sec_derivation (in °C)',
                           legend1='outdoor_weather_bricklet_V2_station_data_temperature (in °C)',
                           legend2='outdoor_weather_bricklet_V2_station_data_humidity (in %)',
                           legend3='outdoor_weather_bricklet_V2_sensor_data_temperature (in °C)',
                           legend4='outdoor_weather_bricklet_V2_sensor_data_humidity (in %)',
                           legend5='ir_bricklet_v2_ambient_temperature (in °C)',
                           legend6='ir_bricklet_v2_object_temperature (in °C)',
                           legend7='co2_V2_bricklet_co2_concentration (in ppm)', legend8='co2_V2_bricklet_co2_temperature (in °C)',
                           legend9='co2_V2_bricklet_co2_humidity (in %)', legend10='humidity_bricklet_V2_humidity (in %)',
                           legend11='humidity_bricklet_V2_temperature (in °C)', legend12='sound_pressure_bricklet_decibel (in dB(Z))',
                           legend13='thermal_imaging_bricklet_average_temperature (in °C)', legend14='thermal_imaging_bricklet_max_temperature (in °C)',
                           legend15='thermal_imaging_bricklet_min_temperature (in °C)',
                           legend16='outdoor_weather_bricklet_V2_station_data_rain (liter since the beginning of recording)',
                           legend17='refraktometer (in %)',
                           labels=tmp[-1],
                           owbsdt_betrag_erst_ab=tmp[0],
                           outdoor_weather_bricklet_V2_station_data_temperature=tmp[1],
                           outdoor_weather_bricklet_V2_station_data_humidity=tmp[2],
                           outdoor_weather_bricklet_V2_station_data_rain=tmp[3],
                           outdoor_weather_bricklet_V2_sensor_data_temperature=tmp[4],
                           outdoor_weather_bricklet_V2_sensor_data_humidity=tmp[5],
                           temperature_ir_bricklet_v2_ambient_temperature=tmp[6],
                           temperature_ir_bricklet_v2_object_temperature=tmp[7],
                           co2_V2_bricklet_co2_concentration=tmp[8],
                           co2_V2_bricklet_co2_temperature=tmp[9],
                           co2_V2_bricklet_co2_humidity=tmp[10],
                           humidity_bricklet_V2_humidity=tmp[11],
                           humidity_bricklet_V2_temperature=tmp[12],
                           sound_pressure_bricklet_decibel=tmp[13],
                           thermal_imaging_bricklet_average_temperature=tmp[14],
                           thermal_imaging_bricklet_max_temperature=tmp[15],
                           thermal_imaging_bricklet_min_temperature=tmp[16],
                           refraktometer_index=tmp[17],
                           refraktometer_value=tmp[18],
                           nav_form=nav_form
                           )

if __name__ == '__main__':
    app.run(host=server_ip, port=server_port)



