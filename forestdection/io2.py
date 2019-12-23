import csv
from typing import List, Tuple, Optional

import matplotlib.pyplot as plt
import numpy as np
from osgeo import gdal

from forestdection.domain import Timeseries, RasterCube, TifInfo
from forestdection.filepath import FilepathProvider


class RasterSegmenter:
    # TODO set from config
    # Do not increase if used with current setup! Max!
    col_size = 2000
    row_size = 2000

    def __init__(self):
        self.col_off = 0
        self.row_off = 0

    def get_next_cube(self, input_paths: List[str]) -> Optional[RasterCube]:
        cube = []
        for path in input_paths:
            ds: gdal.Dataset = gdal.Open(path)

            # Check there is some part of the raster left
            if self.col_off >= ds.RasterXSize:
                self.col_off = 0
                self.row_off += self.row_size
                if self.row_off >= ds.RasterYSize:
                    break

            # Ensure bbox is inside raster
            col_size = self.col_size
            row_size = self.row_size
            if self.col_off + self.col_size >= ds.RasterXSize:
                col_size = ds.RasterXSize - self.col_off
            if self.row_off + self.row_size >= ds.RasterYSize:
                row_size = ds.RasterYSize - self.row_off

            # Get data
            c = np.array(ds.GetRasterBand(1).ReadAsArray(self.col_off, self.row_off, col_size, row_size))
            cube.append(c)

        if not cube:
            return None

        # Order is important! First assign col_off to raster_cube and then increase it for the next cube
        raster_cube = RasterCube(self.col_off, self.row_off, np.dstack(cube))
        self.col_off += self.col_size
        return raster_cube

    def get_raster_from_cubes(self, cubes: List[RasterCube]) -> np.array:
        cols, rows = self._get_size_of_all_cubes(cubes)
        raster = np.empty((rows, cols), dtype=cubes[0].data.dtype)
        raster[:] = np.nan
        for c in cubes:
            col_min, col_max, row_min, row_max = c.get_extend()
            raster[row_min:row_max, col_min:col_max] = c.data
        return raster

    def _get_size_of_all_cubes(self, cubes: List[RasterCube]) -> Tuple[int, int]:
        cubes.sort(key=lambda c: c.col_off and c.row_off)
        max_cube = cubes[-1]
        _, col_max, _, row_max = max_cube.get_extend()
        return col_max, row_max

    def get_rmsd_from_cubes(self, cubes: List[RasterCube]) -> np.array:
        return self.get_raster_from_cubes(cubes)

    def get_pearson_from_cubes(self, cubes: List[RasterCube]) -> np.array:
        return self.get_raster_from_cubes(cubes)


class TifReaderWriter:

    filepath_provider = FilepathProvider()

    # TODO read tif (to reuse already calculated rmsd / pearson)

    def write_rmsd_tif(self, rmsd: np.array, output_path: str, source: TifInfo):
        return self.write_tif(rmsd, output_path, source)

    def write_pearson_tif(self, pearson: np.array, output_path: str, source: TifInfo):
        self.write_tif(pearson, output_path, source)

    def write_tif(self, data: np.array, output_path: str, tif_info: TifInfo):
        # Create Driver
        driver = gdal.GetDriverByName('GTiff')
        # TODO check datatype (origin sig0 mm sixteen bit signed integer > is float 32 enough or do we need float64?)
        out_dataset = driver.Create(output_path, tif_info.size_x, tif_info.size_y, 1, gdal.GDT_Float32)
        out_dataset.SetGeoTransform((tif_info.origin_x, tif_info.pixel_width, 0, tif_info.origin_y, 0, tif_info.pixel_height))

        # set Coordinate system
        out_dataset.SetProjection(tif_info.wkt_projection)

        # Write data
        outband = out_dataset.GetRasterBand(1)
        outband.WriteArray(data)
        outband.FlushCache()

        return out_dataset

    def read_tif(self, input_path: str):
        ds = gdal.Open(input_path)
        return np.array(ds.GetRasterBand(1).ReadAsArray())


class Plotter:

    def plot_multiple_timeseries(self, timeseries: List[Timeseries], figsize: Tuple[int, int] = None, save_path: str = None):
        figsize = figsize if figsize else (10, 10)
        num_ts = len(timeseries)

        x: np.array = None
        ts: Timeseries = Timeseries()
        plt.figure(figsize=figsize)
        for idx, ts in enumerate(timeseries):
            ts_size = ts.get_size()
            x = np.arange(ts_size)

            # TODO ylim should same for all plots
            plt.subplot(num_ts, 1, idx + 1)
            plt.ylabel('Mean sig0')
            plt.title(ts.name)
            plt.xticks([], [])
            plt.plot(x, ts.sig0s)

        plt.xticks(x[::3], ts.dates[::3], rotation=20)
        plt.xlabel('Date')
        if save_path:
            plt.savefig(save_path)
        else:
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
