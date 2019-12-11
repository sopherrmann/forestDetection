import numpy as np


class ForestDetection:

    def get_reference_timeseries(self, shapefile, input_files):
        pass

    def get_rmsd(self, reference, actual):
        pass

    def get_pearson_correlation(self, reference, actual):
        pass


class RasterSegmenter:

    def get_next_cube(self, input_paths):
        pass


class ReferenceUtils:

    def crop_raster(self, shape_path, raster_path):
        pass

    def average(self, raster):
        pass


class TimeseriesBuilder:

    def build_timeseries(self, input_paths):
        pass


class Timeseries:

    def __init__(self, data):
        self.data: np.array = data


class FilepathProvider:

    def __init__(self, base_dir):
        self.base_dir = base_dir

    def get_sig0_mm_dir(self):
        pass

    def get_by_polarisation_from_folder(self, folder, forest_type=None):
        pass

    def get_reference_folder(self, reference_type):
        pass

    def get_result_folder(self, result_type):
        pass


class TifWriter:

    def write_rmsd_tif(self, rmsd):
        pass

    def write_pearson_tif(self, pearson):
        self.write_rmsd_tif(pearson)


class Plotter:

    def plot_single_timeseries(self, timeseries):
        pass

    def plot_multiple_timeseries(self, timeseries):
        pass


class CsvReaderWriter:

    def write_timeseries(self, timeseries, output_path):
        pass

    def read_timeseries(self, input_path):
        pass

