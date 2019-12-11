class RasterSegmenter:

    def get_next_cube(self, input_paths):
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
