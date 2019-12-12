import csv
from typing import List

import matplotlib.pyplot as plt
import numpy as np

from forestdection.domain import Timeseries


class RasterSegmenter:

    def get_next_cube(self, input_paths: List[str]):
        pass


class TifWriter:

    def write_rmsd_tif(self, rmsd):
        pass

    def write_pearson_tif(self, pearson):
        self.write_rmsd_tif(pearson)


class Plotter:

    def plot_single_timeseries(self, timeseries: Timeseries):
        pass

    def plot_multiple_timeseries(self, timeseries: List[Timeseries]):
        num_ts = len(timeseries)

        plt.figure()
        for idx, ts in enumerate(timeseries):
            ts_size = ts.get_size()

            plt.subplot(num_ts, 1, idx+1)
            plt.ylabel('Mean sig0')
            plt.title(ts.name)
            plt.plot(np.linspace(0, ts_size, ts_size), ts.sig0s)
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
