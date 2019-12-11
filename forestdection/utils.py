import os
from typing import List

import pandas as pd


def get_filepath_from_folder(folder: str, file_ext: str) -> List[str]:
    if not os.path.isdir(folder):
        raise Exception(f'The given path {folder} is not a folder')
    return [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(file_ext)]


def get_vv_vh_filepaths(folder: str, file_ext: str = '.tif'):
    all_files = get_filepath_from_folder(folder, file_ext)
    vv = []
    vh = []
    for f in all_files:
        part = os.path.basename(f).split('_')[3]
        if part.endswith('VV-'):
            vv.append(f)
        elif part.split('VH-'):
            vh.append(f)
    return {'VV': vv, 'VH': vh}


def get_date_from_filename(filename: str) -> int:
    date_str = filename.split('_')[0]
    year = date_str[1:5]
    month = date_str[5:7]
    return int(f'{year}{month}')


def write_list_to_csv(data: pd.DataFrame, output_path: str):
    data.to_csv(output_path, index=False, header=True)


def read_csv(path: str, list_per_col: bool = False):
    with open(path, 'r') as f:
        data = pd.read_csv(f)
    if list_per_col:
        return {column_name: data[column_name].tolist() for column_name in data.columns}
    return data
