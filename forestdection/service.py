import subprocess
from typing import List, Tuple

import numpy as np
from osgeo import gdal

from forestdection.domain import Timeseries, Indicators
from forestdection.filepath import FilepathProvider, get_filename_from_path, get_date_from_filename
from forestdection.io2 import RasterSegmenter


class ReferenceUtils:
    filepath_provider = FilepathProvider()

    def crop_raster(self, shape_path: str, input_paths: List[str], output_sufix: str) -> List[str]:
        output_paths = []
        for inraster in input_paths:
            input_filename = get_filename_from_path(inraster)
            outraster = self.filepath_provider.get_cropped_mm_file(input_filename, output_sufix)
            output_paths.append(outraster)
            subprocess.call(['gdalwarp', inraster, outraster, '-cutline', shape_path, '-crop_to_cutline'])
        return output_paths

    def average(self, raster_paths: List[str]) -> Timeseries:
        timeseries = Timeseries()
        raster_paths.sort()
        for raster_path in raster_paths:
            ds = gdal.Open(raster_path)
            avg = np.average(np.array(ds.GetRasterBand(1).ReadAsArray()))

            date_str = get_date_from_filename(get_filename_from_path(raster_path))
            timeseries.push(date_str, avg)
        return timeseries

    def get_reference_timeseries(self, forest_type: str, shape_path: str, input_paths: List[str]) -> Timeseries:
        cropped_mm_paths = self.crop_raster(shape_path, input_paths, forest_type)
        timeseries = self.average(cropped_mm_paths)
        return timeseries


class IndicatorCalculation:

    def get_rmsd(self, reference_timeseries: Timeseries, actual_paths: List[str]) -> np.array:
        rmsd_cubes = []
        raster_segmenter = RasterSegmenter()
        ts_size = reference_timeseries.get_size()

        print(f'Timeseries: {reference_timeseries.get_description()}')
        counter = 1
        cube = raster_segmenter.get_next_cube(actual_paths)
        while cube:
            print(f'RMSD Segment Counter: {counter}')
            timeseries_array = np.array(reference_timeseries.sig0s)
            cube.data = np.square(cube.data - timeseries_array[None, None, :]) # per pixel

            cube.data = np.sqrt(np.sum(cube.data, axis=2) / ts_size)  # combining pixel

            rmsd_cubes.append(cube)
            counter += 1
            cube = raster_segmenter.get_next_cube(actual_paths)

        raster = raster_segmenter.get_rmsd_from_cubes(rmsd_cubes)
        del rmsd_cubes
        return raster

    def get_pearson(self, reference_timeseries: Timeseries, actual_paths: List[str]) -> np.array:
        pearson_cubes = []
        raster_segmenter = RasterSegmenter()

        reference_std, reference_centered = self.get_centered_std_timeseries(reference_timeseries.sig0s)
        print(f'Timeseries: {reference_timeseries.get_description()}')
        counter = 1
        cube = raster_segmenter.get_next_cube(actual_paths)
        while cube:
            print(f'Pearson Segment Counter: {counter}')
            cube.data = self.get_pearson_by_cube(cube.data, reference_std, reference_centered)
            pearson_cubes.append(cube)
            counter += 1
            cube = raster_segmenter.get_next_cube(actual_paths)

        raster = raster_segmenter.get_pearson_from_cubes(pearson_cubes)
        del pearson_cubes
        return raster

    def get_pearson_by_cube(self, cube_data: np.array, reference_std: float, reference_centered: np.array):
        cube_std, cube_centered = self.get_centered_std_cube(cube_data)
        numerator = np.sum(cube_centered * reference_centered, axis=2) / (cube_data.shape[2] - 1)
        denominator = cube_std * reference_std
        cube_data = numerator / denominator
        return cube_data

    def get_centered_std_cube(self, cube_data: np.array):
        size = cube_data.shape[2]
        centered = cube_data - np.average(cube_data, axis=2)[:, :, None]
        std = np.sqrt(np.sum(np.square(centered), axis=2) / (size - 1))
        return std, centered

    def get_centered_std_timeseries(self, data: List[float]) -> Tuple[float, np.array]:
        data = np.array(data)
        centered = data - np.average(data)
        std = np.sqrt(np.sum(np.square(centered)) / (data.shape[0] - 1))
        return std, centered


class ForestClassification:

    def classify_forest(self, rmsd: Indicators, pearson: Indicators):
        # rmsd / pearson are 3D numpy arrays first two dim geographic extend, third are different forest types
        rmsd_vh = rmsd.get_data_by_description(polarization='VH')
        rmsd_vv = rmsd.get_data_by_description(polarization='VV')
        pearson_vh = pearson.get_data_by_description(polarization='VH')
        forest_mask = self._get_forest_mask(rmsd_vh, rmsd_vv, pearson_vh)

        # forest classification based on highest RMSD VH value
        # get index of highest RMSD VH value (0 / 1... first / second forest type)
        forest_type_index_raster = np.argmax(rmsd_vh, axis=2)
        forest_type_index_raster += 1  # now all indexes are above 0

        # 0 ... no forest
        # 1 ... first forest type
        # 2 ... second forest type
        return forest_type_index_raster * forest_mask

    def _get_forest_mask(self, rmsd_vh: np.array, rmsd_vv: np.array, pearson_vh: np.array) -> np.array:
        # RMSD VH < 1.5 dB and RMSD VV < 2.0 dB and Pearson VH > 0.4 -> 1 otherwise 0
        # TODO is a simple comparision enough? RMSD compared to decibel
        mask_rmsd_vh = np.any((rmsd_vh < 1.5), axis=2)
        mask_rmsd_vv = np.any(rmsd_vv < 2.0, axis=2)
        mask_pearson_vh = np.any(pearson_vh > 0.4, axis=2)
        return (mask_rmsd_vh * mask_rmsd_vv * mask_pearson_vh).astype(int)

    def _linear_to_decibel(self, value):
        return 10 * np.log10(value)
