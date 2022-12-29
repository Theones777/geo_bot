import json
import shutil
import zipfile

import gspread
import pandas as pd
import datetime
import os
from gspread_dataframe import set_with_dataframe

from utils.log import logging
from utils.variables import TMP_ARC_PATH, AVAIL_AUD_PROJECTS_NAMES, CHILDREN_DATASET_CSV_PATH, \
    TMP_DOWNLOAD_PATH, IDX_FILENAME_COL, SYNTHESYS_CSV_PATH, VERIFICATION_SOLUTIONS, TXT_JSON_PATH, \
    YD_SYNTHESIS_AUDIO_PATH, SYNTHESIS_DATA_PATH, GOOGLE_SHEET_JSON_PATH
from utils.yd import download_files_from_yd, upload_files_to_yd
from utils.yd_init import y_disk


def insert_incorrect_samples(project_name, marker_id):
    try:
        if project_name == AVAIL_AUD_PROJECTS_NAMES[0]:
            df_path = CHILDREN_DATASET_CSV_PATH
        today = datetime.datetime.today().isoformat(sep=" ").split(' ')[0]
        upload_date = '.'.join([today.split('-')[2], today.split('-')[1], today.split('-')[0]])
        df = pd.read_csv(df_path)

        df.loc[(df['marker_id'] == marker_id) & (df['status'] == 'in_process'), 'done_date'] = upload_date
        df.loc[(df['marker_id'] == marker_id) & (df['status'] == 'in_process'), 'status'] = 'not suitable'

        df.to_csv(CHILDREN_DATASET_CSV_PATH, index=False)
        out_str = 'Некорректные примеры записаны'
    except:
        out_str = 'Ошибка записи'
    return out_str


def get_markup_data(message, examples_num, marker_id, project_name):
    today = datetime.datetime.today().isoformat(sep=" ").split(' ')[0]
    arc_path = os.path.join(TMP_ARC_PATH, f'{today}_{marker_id}.zip')
    if project_name == AVAIL_AUD_PROJECTS_NAMES[0]:

        df = pd.read_csv(CHILDREN_DATASET_CSV_PATH)
        tmp_df = df[df['status'] == 'waiting']
        # if len(tmp_df) < examples_num:
        #     for f in y_disk.listdir(YD_RAW_CHILDREN_PATH):
        #         if f.name.endswith('.wav') and f.name not in df['file_name'].tolist():
        #             df = df.append({'file_name': f.name,
        #                             'status': 'waiting'}, ignore_index=True)
        #     df.to_csv(CHILDREN_DATASET_CSV_PATH, index=False)
        #     tmp_df = df[df['status'] == 'waiting']

        output_files_names = tmp_df.iloc[0:examples_num, IDX_FILENAME_COL].tolist()
        for file_name in output_files_names:
            df.loc[df['file_name'] == file_name, 'status'] = 'coping'
        df.to_csv(CHILDREN_DATASET_CSV_PATH, index=False)

        os.makedirs(os.path.join(TMP_DOWNLOAD_PATH, marker_id), exist_ok=True)
        with zipfile.ZipFile(arc_path, 'w') as myzip:
            for wav_name in output_files_names:
                logging(message, wav_name)
                txt_name = wav_name.replace('.wav', '.txt')
                download_files_from_yd(wav_name, marker_id, project_name)
                logging(message, 'Загрузка успешна')
                myzip.write(os.path.join(TMP_DOWNLOAD_PATH, marker_id, wav_name), arcname=wav_name)
                with open(TXT_JSON_PATH) as j:
                    data = json.load(j)
                el_num = int(txt_name.split('.')[0].split('_')[1])
                el = data[el_num]
                with open(os.path.join(TMP_DOWNLOAD_PATH, marker_id, txt_name), 'w', encoding='utf-8') as f:
                    f.write(el['text'].strip())
                myzip.write(os.path.join(TMP_DOWNLOAD_PATH, marker_id, txt_name), arcname=txt_name)

                df.loc[df['file_name'] == wav_name, 'status'] = 'in_process'
                df.loc[df['file_name'] == wav_name, 'marker_id'] = marker_id

        df.to_csv(CHILDREN_DATASET_CSV_PATH, index=False)
        shutil.rmtree(TMP_DOWNLOAD_PATH)
    return arc_path


def enter_markup_data(message, marker_id, project_name, samples_nums):
    out_str = ''
    sample_count = 0
    if project_name == AVAIL_AUD_PROJECTS_NAMES[0]:
        today = datetime.datetime.today().isoformat(sep=" ").split(' ')[0]
        upload_date = '.'.join([today.split('-')[2], today.split('-')[1], today.split('-')[0]])
        df = pd.read_csv(CHILDREN_DATASET_CSV_PATH)
        files_path = os.path.join(TMP_DOWNLOAD_PATH, marker_id, 'unzip_files')
        for filename in os.listdir(files_path):
            logging(message, filename)
            out_str += upload_files_to_yd(message, files_path, filename)
            if not out_str and filename.endswith('.wav'):
                sample_count += 1
                df.loc[df['file_name'] == filename, 'done_date'] = upload_date
                df.loc[df['file_name'] == filename, 'status'] = 'done'

        df.to_csv(CHILDREN_DATASET_CSV_PATH, index=False)
        out_str += f'Примеры в количестве {sample_count} загружены на Яндекс диск'
    return out_str


def get_synthesis_audio(message, marker_id, project_name):
    df = pd.read_csv(SYNTHESYS_CSV_PATH)
    tmp_df = df[df['status'] == 'waiting']
    # if len(tmp_df) == 0:
        # for f in y_disk.listdir(YD_SYNTHESIS_AUDIO_PATH):
        #     if f.name.endswith('.wav') and f.name not in df['file_name'].tolist():
        #         download_files_from_yd(f.name.replace('.wav', '.txt'), marker_id, project_name)
        #         with open(os.path.join(TMP_DOWNLOAD_PATH, marker_id, f.name.replace('.wav', '.txt')),
        #                   encoding='utf-8') as t:
        #             text = t.read().strip()
        #         df = df.append({'file_name': f.name,
        #                         'status': 'waiting',
        #                         'text': text}, ignore_index=True)
        # df.to_csv(CHILDREN_DATASET_CSV_PATH, index=False)
        # tmp_df = df[df['status'] == 'waiting']

    wav_name = tmp_df.iloc[0, IDX_FILENAME_COL]
    df.loc[df['file_name'] == wav_name, 'status'] = 'coping'
    df.to_csv(SYNTHESYS_CSV_PATH, index=False)

    os.makedirs(os.path.join(TMP_DOWNLOAD_PATH, marker_id), exist_ok=True)
    logging(message, wav_name)

    # download_files_from_yd(wav_name, marker_id, project_name)
    shutil.copy(os.path.join(SYNTHESIS_DATA_PATH, wav_name), os.path.join(TMP_DOWNLOAD_PATH, marker_id, wav_name))
    df.loc[df['file_name'] == wav_name, 'status'] = 'in_process'
    df.loc[df['file_name'] == wav_name, 'marker_id'] = marker_id
    audio_path = os.path.join(TMP_DOWNLOAD_PATH, marker_id, wav_name)
    text = df.loc[df['file_name'] == wav_name, 'text'].tolist()[0]
    df.to_csv(SYNTHESYS_CSV_PATH, index=False)

    return audio_path, text, wav_name


def insert_synthesis_audio_solution(solution, wav_name):
    df = pd.read_csv(SYNTHESYS_CSV_PATH)
    if solution == VERIFICATION_SOLUTIONS[-1]:
        df.loc[df['file_name'] == wav_name, 'status'] = 'waiting'
        df.loc[df['file_name'] == wav_name, 'marker_id'] = ''
        df.to_csv(SYNTHESYS_CSV_PATH, index=False)
        gc = gspread.service_account(filename=GOOGLE_SHEET_JSON_PATH)
        timetable = gc.open('Geodata')
        time_worksheet = timetable.worksheet('Synthesis')
        set_with_dataframe(time_worksheet, df)
    else:
        status_dict = {VERIFICATION_SOLUTIONS[0]: 'done',
                       VERIFICATION_SOLUTIONS[1]: 'unsuitable'}
        today = datetime.datetime.today().isoformat(sep=" ").split(' ')[0]
        upload_date = '.'.join([today.split('-')[2], today.split('-')[1], today.split('-')[0]])
        df.loc[df['file_name'] == wav_name, 'done_date'] = upload_date
        df.loc[df['file_name'] == wav_name, 'status'] = status_dict[solution]
        df.to_csv(SYNTHESYS_CSV_PATH, index=False)
