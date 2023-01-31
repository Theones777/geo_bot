import shutil

import gspread
import pandas as pd
import datetime
import os
from gspread_dataframe import set_with_dataframe

from utils.log import logging
from utils.variables import TMP_DOWNLOAD_PATH, IDX_FILENAME_COL, SYNTHESYS_CSV_PATH, VERIFICATION_SOLUTIONS, \
    SYNTHESIS_DATA_PATH, GOOGLE_SHEET_JSON_PATH, GEO_TABLE_NAME


def get_synthesis_audio(message, marker_id):
    df = pd.read_csv(SYNTHESYS_CSV_PATH)
    tmp_df = df[df['status'] == 'waiting']
    wav_name = tmp_df.iloc[0, IDX_FILENAME_COL]
    df.loc[df['file_name'] == wav_name, 'status'] = 'coping'
    df.to_csv(SYNTHESYS_CSV_PATH, index=False)

    logging(message, wav_name)

    df.loc[df['file_name'] == wav_name, 'status'] = 'in_process'
    df.loc[df['file_name'] == wav_name, 'marker_id'] = marker_id
    audio_path = os.path.join(SYNTHESIS_DATA_PATH, wav_name)
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
        timetable = gc.open(GEO_TABLE_NAME)
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
