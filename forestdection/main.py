import os
from typing import List
import numpy as np

from forestdection.filepath import FilepathProvider, FilenameProvider, get_filepath
from forestdection.service import IndicatorCalculation, ReferenceUtils
from forestdection.io import CsvReaderWriter, TifReaderWriter, Plotter
from forestdection.domain import Timeseries, TifInfo


class Main:

    filepath_provider = FilepathProvider()
    filename_provider = FilenameProvider()
    indicator_calculation = IndicatorCalculation()
    csv_read_writer = CsvReaderWriter()
    tif_reader_writer = TifReaderWriter()
    reference_utils = ReferenceUtils()
    plotter = Plotter()

    def get_all_reference_timeseries(self, build: bool = False, plot: bool = False) -> List[Timeseries]:
        shape_paths = self.filepath_provider.get_input_shape_files_by_forest_type()
        all_mm_paths = self.filepath_provider.get_input_mm_files_by_polarisation()

        all_timeseries = []
        for forest_type, shape_path in shape_paths.items():
            for polarization, mm_paths in all_mm_paths.items():
                timeseries_path = self.filepath_provider.get_timeseries_file(polarization, forest_type)

                if not os.path.isfile(timeseries_path) or build:
                    timeseries = self.reference_utils.get_reference_timeseries(forest_type, shape_path, mm_paths)
                    self.csv_read_writer.write_timeseries(timeseries, timeseries_path)
                else:
                    timeseries = self.csv_read_writer.read_timeseries(timeseries_path)

                timeseries.set_name(self.filename_provider.get_timeseries_name(polarization, forest_type))
                all_timeseries.append(timeseries)

        if plot:
            plot_path = get_filepath(self.filepath_provider.get_plot_folder(), 'reference_timeseries.png')
            self.plotter.plot_multiple_timeseries(all_timeseries, save_path=plot_path)

        return all_timeseries

    def get_all_rmsd(self, build: bool = False) -> List[np.array]:
        return self._get_indicator_for_all(self.filepath_provider.get_rmsd_file, self.indicator_calculation.get_rmsd, build)

    def get_all_pearson(self, build: bool = False) -> List[np.array]:
        return self._get_indicator_for_all(self.filepath_provider.get_pearson_file, self.indicator_calculation.get_pearson, build)

    def _get_indicator_for_all(self, indicator_path_func, indicator_func, build: bool = False) -> List[np.array]:
        all_reference_timeseries = self.get_all_reference_timeseries()
        all_mm_paths = self.filepath_provider.get_input_mm_files_by_polarisation()
        mm_tif_info = TifInfo(all_mm_paths['VV'][0])

        indicator_timeseries = []
        for reference_timeseries in all_reference_timeseries:
            polarization, forest_type = self.filename_provider.get_info_from_name(reference_timeseries.name)
            indicator_path = indicator_path_func(polarization, forest_type)

            if not os.path.isfile(indicator_path) or build:
                indicator = indicator_func(reference_timeseries, all_mm_paths[polarization])
                self.tif_reader_writer.write_tif(indicator, indicator_path, mm_tif_info)
            else:
                indicator = self.tif_reader_writer.read_tif(indicator_path)

            indicator_timeseries.append(indicator)
        return indicator_timeseries


if __name__ == '__main__':
    pass
