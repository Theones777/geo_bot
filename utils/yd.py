import json
import os

import yadisk as yadisk

from utils.log import logging
from utils.variables import AVAIL_AUD_PROJECTS_NAMES, YD_DONE_CHILDREN_PATH, TMP_DOWNLOAD_PATH, YD_TOKEN, \
    YD_RAW_AUDIO_CHILDREN_PATH, TXT_JSON_PATH, YD_SYNTHESIS_AUDIO_PATH
from utils.yd_init import y_disk


def get_text(sample, project_name):
    txt_file = f"{sample.split('.')[0]}.txt"
    if project_name == AVAIL_AUD_PROJECTS_NAMES[0]:
        checked_file = f"{YD_DONE_CHILDREN_PATH}/{txt_file}"

    y_disk.download(checked_file, os.path.join(TMP_DOWNLOAD_PATH, txt_file))
    with open(os.path.join(TMP_DOWNLOAD_PATH, txt_file), encoding='utf-8') as f:
        text = f.read()
    os.remove(os.path.join(TMP_DOWNLOAD_PATH, txt_file))
    return text


def download_files_from_yd(wav_name, marker_id, project_name):
    if project_name == AVAIL_AUD_PROJECTS_NAMES[0]:
        source_wav_path = f'{YD_RAW_AUDIO_CHILDREN_PATH}/{wav_name}'
    else:
        source_wav_path = f'{YD_SYNTHESIS_AUDIO_PATH}/{wav_name}'
    try:
        y_disk.download(source_wav_path, os.path.join(TMP_DOWNLOAD_PATH, marker_id, wav_name))
    except:
        print(wav_name)


def upload_files_to_yd(message, files_path, filename):
    out_str = ''
    result_path = f'{YD_DONE_CHILDREN_PATH}/{filename}'
    try:
        y_disk.upload(os.path.join(files_path, filename), result_path)
        logging(message, 'Успешная загрузка на ЯД')
    except yadisk.exceptions.ParentNotFoundError:
        return 'Нужная папка не найдена'
    except yadisk.exceptions.PathExistsError:
        out_str += f'Файл {filename} уже загружен!\n'

    return out_str
