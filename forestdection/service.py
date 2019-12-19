import subprocess
from typing import List

import numpy as np
from osgeo import gdal, osr

from forestdection.domain import Timeseries, TifInfo
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

    def get_pearson_correlation(self, reference, actual):
        pass


class TimeseriesBuilder:

    def build_timeseries(self, input_paths):
        pass
