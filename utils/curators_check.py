import gspread
import pandas as pd

from utils.log import logging
from utils.variables import AVAIL_AUD_PROJECTS_NAMES, GOOGLE_SHEET_JSON_PATH, CURATORS_TABLE_NAME, CURATORS_COORDINATES, \
    CHILDREN_DATASET_CSV_PATH
from utils.yd import get_text


def get_marker_id(sample, project_name):
    if project_name == AVAIL_AUD_PROJECTS_NAMES[0]:
        df = pd.read_csv(CHILDREN_DATASET_CSV_PATH)
    marker_id = df.loc[df['file_name'] == sample, 'marker_id'].tolist()[0]
    upload_date = df.loc[df['file_name'] == sample, 'done_date'].tolist()[0]
    return marker_id, upload_date


def insert_mistakes_info(mistakes_info, upload_date, marker_id):
    gc = gspread.service_account(filename=GOOGLE_SHEET_JSON_PATH)
    sh = gc.open(CURATORS_TABLE_NAME)
    worksheet = sh.worksheet(marker_id)
    cell = worksheet.find(upload_date)
    mistakes_num_col = CURATORS_COORDINATES['handle_num_mistakes_col']
    mistakes_col = CURATORS_COORDINATES['handle_mistakes_col']

    if worksheet.cell(cell.row, mistakes_num_col).value:
        mistakes_num = int(worksheet.cell(cell.row, mistakes_num_col).value)
        mistakes = worksheet.cell(cell.row, mistakes_col).value
    else:
        mistakes_num = 0
        mistakes = ''

    mistakes_num += 1
    mistakes += '\n' + mistakes_info
    worksheet.update_cell(cell.row, mistakes_num_col, mistakes_num)
    worksheet.update_cell(cell.row, mistakes_col, mistakes)


def enter_curator_data(message, sample, project_name):
    curator_info = message.text
    try:
        marker_id, upload_date = get_marker_id(sample, project_name)
    except:
        return 'Не удалось получить данные из таблицы'

    logging(message, marker_id)

    try:
        text = get_text(sample, project_name)
    except:
        return 'Не удалось загрузить файл с Яндекс диска'

    logging(message, text)

    try:
        mistakes_info = '-'.join([text, curator_info])
        insert_mistakes_info(mistakes_info, upload_date, marker_id)
    except:
        return 'Не удалось занести данные в таблицу кураторов'

    return 'Данные занесены в таблицу ошибок'
