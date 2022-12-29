import os
import re
import zipfile

from utils.variables import TMP_DOWNLOAD_PATH


def check_file(file_path, txt_file):
    out_str = ''
    with open(file_path, 'r', encoding='utf-8') as file_markup:
        for string in file_markup.readlines():
            errors = [txt_file]
            if len(string.strip()) > 0:
                if re.findall('\d', string.strip()):
                    errors.append('ненормализованные цифры')
                if re.findall('[a-zA-Z]', string.strip()):
                    errors.append('латиница')
                    latin_letters = re.findall('[a-zA-Z]', string.strip())
                    for latin_letter in latin_letters:
                        latin_index_start = str(string.strip().index(latin_letter) + 1)
                        latin_index_end = str(int(latin_index_start) + (len(latin_letter)))
                        metastr = f'{latin_letter}: ({latin_index_start}-{latin_index_end})'
                        errors.append(metastr)
                if re.findall('\. [а-я]', string.strip()):
                    errors.append('после точки маленькая буква')
                if re.findall(': [А-Я]', string.strip()):
                    errors.append('возможен обрыв контекста')
                if re.findall('[А-Я]{2,}', string.strip()):
                    errors.append('возможна аббревиатура')
                if re.findall('[\?!,]\.', string.strip()):
                    errors.append('двойные знаки препинания')
                if re.findall('[\?!,\.][А-Яа-я]', string.strip()):
                    errors.append('отсутствует пробел после знака препинания')

                change_count = 0
                if re.findall('\w \.', string.strip()):
                    change_count += 1
                if re.findall('\w \?', string.strip()):
                    change_count += 1
                if re.findall('\w !', string.strip()):
                    change_count += 1
                if re.findall('\w ,', string.strip()):
                    change_count += 1
                if re.findall('\s{2,}', string.strip()):
                    change_count += 1

                if change_count != 0:
                    errors.append('Найдено лишних пробелов: ' + str(change_count))
                out_str += ', '.join(errors) + '\n'
    return out_str


def check_input_files(archive_path, marker_id):
    check_report = ''
    files_path = os.path.join(TMP_DOWNLOAD_PATH, marker_id, 'unzip_files')
    os.makedirs(files_path, exist_ok=True)
    with zipfile.ZipFile(archive_path) as zf:
        zf.extractall(files_path)

    samples_nums = len(os.listdir(files_path)) / 2
    txt_files = [fl for fl in os.listdir(files_path) if fl.endswith('.txt')]
    for txt_file in txt_files:
        check_report += check_file(os.path.join(files_path, txt_file), txt_file) + '\n'
    if not check_report:
        check_report = 'Ошибок не найдено'
    return check_report, samples_nums
