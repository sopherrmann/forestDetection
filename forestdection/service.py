import subprocess

import numpy as np
from osgeo import gdal

from forestdection.domain import Timeseries
from forestdection.filepath import FilepathProvider, get_filename_from_path
from forestdection.utils import get_date_from_filename


class ReferenceUtils:
    filepath_provider = FilepathProvider()

    def crop_raster(self, shape_path, raster_paths, output_sufix):
        for inraster in raster_paths:
            input_filename = get_filename_from_path(inraster)
            outraster = self.filepath_provider.get_cropped_mm_file(input_filename, output_sufix)
            subprocess.call(['gdalwarp', inraster, outraster, '-cutline', shape_path, '-crop_to_cutline'])

        return self.filepath_provider.get_cropped_mm_folder()

    def average(self, raster_paths):
        timeseries = Timeseries()
        raster_paths.sort()
        for raster_path in raster_paths:
            date_str = get_date_from_filename(get_filename_from_path(raster_path))
            ds = gdal.Open(raster_path)
            avg = np.average(np.array(ds.GetRasterBand(1).ReadAsArray()))

            timeseries.push(date_str, avg)
        return timeseries


class ForestDetection:
    reference_utils = ReferenceUtils()

    def get_reference_timeseries(self, forest_type_shape_tuples, input_paths):
        for forest_type, shape_path in forest_type_shape_tuples:
            self.reference_utils.crop_raster(shape_path, input_paths, forest_type)

    def get_rmsd(self, reference, actual):
        pass

    def get_pearson_correlation(self, reference, actual):
        pass


class TimeseriesBuilder:

    def build_timeseries(self, input_paths):
        pass
