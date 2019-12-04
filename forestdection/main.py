import os
import subprocess
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from osgeo import gdal

from forestdection.utils import write_list_to_csv, get_filepath_from_folder, get_date_from_filename, read_csv, \
    get_vv_vh_filepaths


class ForestDetection:

    def __init__(self, base_dir: str):
        self.base_dir = base_dir

        # Sig0 Monthly Mean
        self.mm_dir = os.path.join(self.base_dir, 'sig0_montly_mean')
        self.mm_paths = get_filepath_from_folder(self.mm_dir, '.tif')

        # Reference area data
        self.mm_cropped_dir = os.path.join(self.base_dir, 'reference_area', 'cropped_mm')
        self.shape_dir = os.path.join(self.base_dir, 'reference_area', 'shape')
        self.ref_time_dir = os.path.join(self.base_dir, 'reference_area', 'timeseries')

        self.forest_types = self.get_forest_types()

    def create_reference_timeseries(self):
        # TODO add if to check if cropped datasets already exit or if they have to get created first
        shape_paths = self.get_filepath_from_folder(self.shape_dir, '.shp')
        self.crop_to_shape(input_paths=self.mm_paths, output_folder=self.mm_cropped_dir, shape_paths=shape_paths)

        for ft in self.forest_types:
            paths = get_vv_vh_filepaths(os.path.join(self.mm_cropped_dir, ft))
            for polarisation, pola_paths in paths.items():
                mm_crop_avg = self.get_avg_per_ds(pola_paths)
                mm_crop_avg_file = os.path.join(self.ref_time_dir, f'timeseries_{polarisation}_{ft}.csv')
                write_list_to_csv(mm_crop_avg, mm_crop_avg_file)

    def crop_to_shape(self, input_paths: List[str], output_folder: str, shape_paths: List[str]):
        for shape in shape_paths:
            forest_type = self.get_forest_types_from_filename(shape)
            output_folder_forest = os.path.join(output_folder, forest_type)
            if not os.path.isdir(output_folder_forest):
                os.mkdir(output_folder_forest)

            for inraster in input_paths:
                in_filename = os.path.basename(inraster)
                outraster = os.path.join(output_folder_forest, in_filename.replace('.tif', f'_{forest_type}.tif'))
                subprocess.call(['gdalwarp', inraster, outraster, '-cutline', shape, '-crop_to_cutline'])

    def get_forest_types(self):
        shape_paths = get_filepath_from_folder(self.shape_dir, '.shp')
        return [self.get_forest_types_from_filename(s) for s in shape_paths]

    @staticmethod
    def get_forest_types_from_filename(name: str) -> str:
        return os.path.basename(name).split('.')[0].replace(' ', '_')

    @staticmethod
    def get_avg_per_ds(filepaths: List[str]) -> pd.DataFrame:
        data = {'date': [], 'sig0': []}
        filepaths.sort()
        for f in filepaths:
            date_str = get_date_from_filename(os.path.basename(f))
            ds = gdal.Open(f)
            avg = np.average(np.array(ds.GetRasterBand(1).ReadAsArray()))
            data['date'].append(date_str)
            data['sig0'].append(avg)
        return pd.DataFrame(data)

    def plot_ref_timeseries(self):
        time_paths = get_filepath_from_folder(self.ref_time_dir, '.csv')
        num_time = len(time_paths)

        plt.figure()
        for idx, time_path in enumerate(time_paths):
            part = os.path.basename(time_path).split('.')[0]
            ft = part.split('_')[-1]
            pola = part.split('_')[-2]
            data = read_csv(time_path, list_per_col=True)

            plt.subplot(num_time, 1, idx+1)
            plt.ylabel('Mean Sig0')
            plt.title(f'{ft} - {pola}')
            plt.plot(np.linspace(0, 36, 36), data['sig0'])
        plt.show()


if __name__ == '__main__':
    src = '/shares/mfue1/teaching/stu_scratch/Microwave_Remote_Sensing/Group1/00_inputdata/'
    FD = ForestDetection(base_dir=src)
    FD.create_reference_timeseries()
    FD.plot_ref_timeseries()
