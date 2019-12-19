import subprocess
from typing import List

import numpy as np
from osgeo import gdal, osr

from forestdection.domain import Timeseries, RasterCube
from forestdection.filepath import FilepathProvider, get_filename_from_path, get_date_from_filename
from forestdection.io import RasterSegmenter


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


class ForestDetection:
    reference_utils = ReferenceUtils()

    # iteration over forest type and polarization should be handled separately
    def get_reference_timeseries(self, forest_type: str, shape_path: str, input_paths: List[str]) -> Timeseries:
        cropped_mm_paths = self.reference_utils.crop_raster(shape_path, input_paths, forest_type)
        timeseries = self.reference_utils.average(cropped_mm_paths)
        return timeseries

    def get_rmsd(self, reference_timeseries: Timeseries, actual_paths: List[str]):
        rmsd_cubes = []
        raster_segmenter = RasterSegmenter()
        ts_size = reference_timeseries.get_size()

        print(f'\nTimeseries: {reference_timeseries.name}')
        counter = 1
        cube = raster_segmenter.get_next_cube(actual_paths)
        while cube:
            print(f'RMSD Segment Counter: {counter}')
            timeseries_array = np.array(reference_timeseries.sig0s)
            cube.data = np.square(cube.data - timeseries_array)  # per pixel
            cube.data = np.sqrt(np.sum(cube.data, axis=2) / ts_size)  # combining pixel

            rmsd_cubes.append(cube)
            counter += 1
            cube = raster_segmenter.get_next_cube(actual_paths)

        raster = raster_segmenter.get_rmsd_from_cubes(rmsd_cubes)
        del rmsd_cubes
        return raster

        return raster_segmenter.get_rmsd_from_cubes(rmsd)

    def get_pearson(self, reference_timeseries: Timeseries, actual_paths: List[str]):
        pearson_cubes = []
        raster_segmenter = RasterSegmenter()

        reference_std, reference_centered = self._get_centered_std_timeseries(reference_timeseries.sig0s)
        cube = raster_segmenter.get_next_cube(actual_paths)
        while cube:
            cube_std, cube_centered = self._get_centered_std_cube(cube)
            numerator = np.sum(cube_centered * reference_centered) / (cube.data.shape[2] - 1)
            denominator = cube_std * reference_std
            cube.data = numerator / denominator

            pearson_cubes.append(cube)
            cube = raster_segmenter.get_next_cube(actual_paths)

        raster = raster_segmenter.get_pearson_from_cubes(pearson_cubes)
        del pearson_cubes
        return raster

    def _get_centered_std_cube(self, cube: RasterCube):
        size = cube.data.shape[2]
        centered = cube.data - np.average(cube.data, axis=2)
        std = np.sqrt(np.sum(np.square(centered), axis=2) / (size - 1))
        return std, centered

    def _get_centered_std_timeseries(self, data: List[float]):
        data = np.array(data)
        centered = data - np.average(data)
        std = np.sqrt(np.sum(np.square(centered)) / (data.shape[0] - 1))
        return std, centered


class TimeseriesBuilder:

    def build_timeseries(self, input_paths):
        pass
