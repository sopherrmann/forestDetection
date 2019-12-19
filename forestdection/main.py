import os
from typing import List

from forestdection.filepath import FilepathProvider, FilenameProvider
from forestdection.service import ForestDetection
from forestdection.io import CsvReaderWriter, TifWriter
from forestdection.domain import Timeseries, TifInfo


class Main:

    filepath_provider = FilepathProvider()
    filename_provider = FilenameProvider()
    forest_detection = ForestDetection()
    csv_read_writer = CsvReaderWriter()
    tif_writer = TifWriter()

    def get_all_reference_timeseries(self, build: bool = False) -> List[Timeseries]:
        shape_paths = self.filepath_provider.get_input_shape_files_by_forest_type()
        all_mm_paths = self.filepath_provider.get_input_mm_files_by_polarisation()

        all_timeseries = []
        for forest_type, shape_path in shape_paths.items():
            for polarization, mm_paths in all_mm_paths.items():
                timeseries_path = self.filepath_provider.get_timeseries_file(polarization, forest_type)

                if not os.path.isfile(timeseries_path) or build:
                    timeseries = self.forest_detection.get_reference_timeseries(forest_type, shape_path, mm_paths)
                    self.csv_read_writer.write_timeseries(timeseries, timeseries_path)
                else:
                    timeseries = self.csv_read_writer.read_timeseries(timeseries_path)

                timeseries.set_name(self.filename_provider.get_timeseries_name(polarization, forest_type))
                all_timeseries.append(timeseries)

        return all_timeseries

    def get_all_rmsd(self, build: bool = False):
        all_reference_timeseries = self.get_all_reference_timeseries()
        all_mm_paths = self.filepath_provider.get_input_mm_files_by_polarisation()
        mm_tif_info = TifInfo(all_mm_paths['VV'][0])

        rmsd_per_timeseries = []
        for reference_timeseries in all_reference_timeseries:
            polarization, forest_type = self.filename_provider.get_info_from_name(reference_timeseries.name)
            rmsd_path = self.filepath_provider.get_rmsd_file(polarization, forest_type)

            if not os.path.isfile(rmsd_path) or build:
                rmsd = self.forest_detection.get_rmsd(reference_timeseries, all_mm_paths[polarization])
                self.tif_writer.write_rmsd_tif(rmsd, rmsd_path, mm_tif_info)
            else:
                # TODO missing TifReader
                rmsd = None

            rmsd_per_timeseries.append(rmsd)
        return rmsd_per_timeseries

    def get_all_pearson(self, build: bool = False):
        pass


if __name__ == '__main__':
    pass
