import gspread as gspread

from utils.variables import GOOGLE_SHEET_JSON_PATH

gc = gspread.service_account(filename=GOOGLE_SHEET_JSON_PATH)


def insert_curator_info(info_to_insert, handle_mistakes_num, upload_date, page_marker_id):
    sh = gc.open(CURATORS_TABLE_NAME)
    worksheet = sh.worksheet(page_marker_id)
    if len(upload_date.split('.')[0]) == 1:
        upload_date = '0' + upload_date
    if len(upload_date.split('.')[1]) == 1:
        upload_date = '.'.join([upload_date.split('.')[0], '0' + upload_date.split('.')[1], upload_date.split('.')[2]])
    cell = worksheet.find(upload_date)
    mistakes_num_col = CURATORS_COORDINATES['handle_num_mistakes_col']
    mistakes_col = CURATORS_COORDINATES['handle_mistakes_col']

    while worksheet.cell(cell.row, mistakes_num_col).value:
        time.sleep(1)
        mistakes_num_col += 2
        mistakes_col += 2
    worksheet.update_cell(cell.row, mistakes_num_col, handle_mistakes_num)
    worksheet.update_cell(cell.row, mistakes_col, info_to_insert)