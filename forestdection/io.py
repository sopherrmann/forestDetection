import csv
from typing import List

import matplotlib.pyplot as plt
import numpy as np
from osgeo import gdal

from forestdection.domain import Timeseries, RasterCube, TifInfo
from forestdection.filepath import FilepathProvider, get_filepath


class RasterSegmenter:
    # TODO set from config
    xsize = 100
    ysize = 100

    def __init__(self):
        self.xoff = 0
        self.yoff = 0

    def get_next_cube(self, input_paths: List[str]):
        cube = []
        for path in input_paths:
            ds: gdal.Dataset = gdal.Open(path)

            if self.xoff > ds.RasterXSize:
                self.xoff = 0
                self.yoff += self.ysize
                if self.yoff > ds.RasterYSize:
                    break

            c = np.array(ds.GetRasterBand(1) \
                         .ReadAsArray(xoff=self.xoff, yoff=self.yoff, xsize=self.xsize, ysize=self.ysize))
            cube.append(c)

        if not cube:
            return None
        self.xoff += self.xsize
        return RasterCube(self.xoff, self.yoff, np.dstack(cube))

    def write_rmsd_from_cubes(self, cubes: List[RasterCube]):
        self.get_raster_from_cubes(cubes)

    def get_raster_from_cubes(self, cubes: List[RasterCube]):
        pass


class TifWriter:

    filepath_provider = FilepathProvider()

    # TODO maybe output path should be given directly
    def write_rmsd_tif(self, rmsd: np.array, output_file: str, source: TifInfo):
        output_folder = self.filepath_provider.get_result_folder('rmsd')
        output_path = get_filepath(output_folder, output_file)

        return self.write_tif(rmsd, output_path, source)

    def write_pearson_tif(self, pearson: np.array, output_file: str, source: TifInfo):
        output_folder = self.filepath_provider.get_result_folder('pearson')
        output_path = get_filepath(output_folder, output_file)

        self.write_tif(pearson, output_path, source)

    def write_tif(self, data: np.array, output_path: str, tif_info: TifInfo):
        # Create Driver
        driver = gdal.GetDriverByName('GTiff')
        out_dataset = driver.Create(output_path, tif_info.size_x, tif_info.size_y, 1, gdal.GDT_Byte)
        out_dataset.SetGeoTransform((tif_info.origin_x, tif_info.pixel_width, 0, tif_info.origin_y, 0, tif_info.pixel_height))

        # set Coordinate system
        out_dataset.SetProjection(tif_info.wkt_projection)

        # Write data
        outband = out_dataset.GetRasterBand(1)
        outband.WriteArray(data)
        outband.FlushCache()

        return out_dataset


class Plotter:

    def plot_single_timeseries(self, timeseries: Timeseries):
        pass

    def plot_multiple_timeseries(self, timeseries: List[Timeseries]):
        num_ts = len(timeseries)

        plt.figure()
        for idx, ts in enumerate(timeseries):
            ts_size = ts.get_size()
            x = np.arange(ts_size)

            plt.subplot(num_ts, 1, idx + 1)
            plt.ylabel('Mean sig0')
            plt.title(ts.name)
            plt.xticks(x, ts.dates, rotation=20)
            plt.plot(x, ts.sig0s)

        plt.xlabel('Date')
        plt.show()


class CsvReaderWriter:

    def write_timeseries(self, timeseries: Timeseries, output_path: str):
        data = list(timeseries.get_zip())
        field_names = timeseries.get_attributes()
        with open(output_path, 'wt') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(field_names)
            for ts in data:
                writer.writerow(ts)

    def read_timeseries(self, input_path) -> Timeseries:
        timeseries = Timeseries()
        with open(input_path, 'r') as file:
            reader = csv.reader(file, delimiter=',')
            line_count = 0
            for row in reader:
                if line_count > 0:
                    timeseries.push(*row)
                line_count += 1
        return timeseries
