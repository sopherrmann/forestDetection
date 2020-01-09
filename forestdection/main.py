import os
from typing import List
import numpy as np

from forestdection.filepath import FilepathProvider, FilenameProvider, get_filepath
from forestdection.service import IndicatorCalculation, ReferenceUtils, ForestClassification
from forestdection.io2 import CsvReaderWriter, TifReaderWriter, Plotter
from forestdection.domain import Timeseries, TifInfo, Indicators


class Main:

    filepath_provider = FilepathProvider()
    filename_provider = FilenameProvider()
    indicator_calculation = IndicatorCalculation()
    forest_classification = ForestClassification()
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

                timeseries.set_description(polarization, forest_type)
                all_timeseries.append(timeseries)

        if plot:
            plot_path = get_filepath(self.filepath_provider.get_plot_folder(), 'reference_timeseries.png')
            self.plotter.plot_multiple_timeseries(all_timeseries, save_path=plot_path)

        return all_timeseries

    def get_all_rmsd(self, build: bool = False) -> Indicators:
        return self._get_indicator_for_all('rmsd', self.filepath_provider.get_rmsd_file, self.indicator_calculation.get_rmsd, build)

    def get_all_pearson(self, build: bool = False) -> Indicators:
        return self._get_indicator_for_all('pearson', self.filepath_provider.get_pearson_file, self.indicator_calculation.get_pearson, build)

    def get_classified(self, build: bool = False) -> List[np.array]:
        rmsd = self.get_all_rmsd()
        pearson = self.get_all_pearson()
        classified_path = self.filepath_provider.get_classified_file()

        if not os.path.isfile(classified_path) or build:
            all_mm_paths = self.filepath_provider.get_input_mm_files_by_polarisation()
            mm_tif_info = TifInfo(all_mm_paths['VV'][0])

            print('Calculating classification tif')
            forest_class_raster = self.forest_classification.classify_forest(rmsd, pearson)
            self.tif_reader_writer.write_tif(forest_class_raster, classified_path, mm_tif_info)
        else:
            print('Loading classified tif')
            forest_class_raster = self.tif_reader_writer.read_tif(classified_path)

        return forest_class_raster

    def _get_indicator_for_all(self, indicator_type: str, indicator_path_func, indicator_func, build: bool = False) -> Indicators:
        all_reference_timeseries = self.get_all_reference_timeseries()
        all_mm_paths = self.filepath_provider.get_input_mm_files_by_polarisation()
        mm_tif_info = TifInfo(all_mm_paths['VV'][0])

        indicators = Indicators()
        for reference_timeseries in all_reference_timeseries:
            forest_type, polarization = reference_timeseries.polarization, reference_timeseries.forest_type
            indicator_path = indicator_path_func(polarization, forest_type)
            print(f'\nCurrent indicator path {indicator_path}')

            if not os.path.isfile(indicator_path) or build:
                print('Calculating tif')
                indicator = indicator_func(reference_timeseries, all_mm_paths[polarization])
                self.tif_reader_writer.write_tif(indicator, indicator_path, mm_tif_info)

            else:
                print('Loading tif')
                indicator = self.tif_reader_writer.read_tif(indicator_path)

            indicators.push(forest_type, polarization, indicator_type, indicator)
        return indicators

    def check_result(self, build: bool = False):
        _ = self.get_classified(build)
        copernicus_hlr_path = self.filepath_provider.get_copernicus_hlr_file()
        classified_path = self.filepath_provider.get_classified_file()
        classified_reprojected_path = self.filepath_provider.get_reprojected_classified_file()

        self.tif_reader_writer.reproject_tif(classified_path, classified_reprojected_path, copernicus_hlr_path)


if __name__ == '__main__':
    m = Main()
    m.get_classified(build=True)
