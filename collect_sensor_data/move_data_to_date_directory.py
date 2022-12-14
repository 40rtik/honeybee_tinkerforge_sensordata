import os
import shutil
import glob


export_root_path = '../flask-web-server/example/dataset'

import_root_path_list = list()
import_root_path_list.append('data')


def readFiles():
    fileListJson = list()
    fileListPng = list()
    for d in import_root_path_list:
        fileListJson.extend(glob.glob(d + str(os.sep) + '*.json'))
        fileListPng.extend(glob.glob(d + str(os.sep) + '*.png'))
    return fileListJson, fileListPng


if __name__ == '__main__':
    jsons, pngs = readFiles()
    print('Jsons: ' + str(len(jsons)))

    for jf in jsons:
        fp = jf.split('thermal_image_')
        create_date = fp[1].split(' ')[0]

        if not os.path.exists(export_root_path + str(os.sep) + create_date):
            os.mkdir(export_root_path + str(os.sep) + create_date)

        shutil.move(jf, export_root_path + str(os.sep) + create_date + str(os.sep) + 'sensor_data_' + fp[1])

    for png in pngs:
        fp = png.split('thermal_image_')
        create_date = fp[1].split(' ')[0]

        if not os.path.exists(export_root_path + str(os.sep) + create_date):
            os.mkdir(export_root_path + str(os.sep) + create_date)

        shutil.move(png, export_root_path + str(os.sep) + create_date + str(os.sep) + 'sensor_data_' + fp[1])
