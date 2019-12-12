import subprocess

from typing import List, Tuple
import numpy as np
from osgeo import gdal

from forestdection.domain import Timeseries
from forestdection.filepath import FilepathProvider, get_filename_from_path, get_date_from_filename


class ReferenceUtils:
    filepath_provider = FilepathProvider()

    def crop_raster(self, shape_path: str, raster_paths: List[str], output_sufix: str) -> List[str]:
        output_paths = []
        for inraster in raster_paths:
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

    def get_reference_timeseries(self, forest_type_shape_tuples: List[Tuple[str, str]], input_paths: List[str])\
            -> List[Timeseries]:
        timeseries_list = []
        for forest_type, shape_path in forest_type_shape_tuples:
            cropped_mm_paths = self.reference_utils.crop_raster(shape_path, input_paths, forest_type)

            timeseries = self.reference_utils.average(cropped_mm_paths)
            timeseries.update_name(forest_type)
            timeseries_list.append(timeseries)
            # TODO need to add polarisation
        return timeseries_list

    def get_rmsd(self, reference_timeseries: Timeseries, actual_paths: List[str]):
        pass

    def get_pearson_correlation(self, reference, actual):
        pass


class TimeseriesBuilder:

    def build_timeseries(self, input_paths):
        pass
