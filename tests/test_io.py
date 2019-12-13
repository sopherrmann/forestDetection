from osgeo import gdal
import numpy as np

from forestdection.io import CsvReaderWriter, TifWriter
from forestdection.domain import Timeseries, TifInfo
from forestdection.filepath import FilepathProvider, get_filepath

filepath_provider = FilepathProvider()
test_folder = filepath_provider.get_test_folder()


def test_csv_read_write():
    # Paths
    output_path = get_filepath(test_folder, 'csv_read_write.csv')

    # timeseries
    dates = ['201901', '201902', '201801', '201807']
    sig0 = [12345, 3452, 12345, 9875]
    input_timeseries = Timeseries(dates, sig0)

    csv_read_writer = CsvReaderWriter()
    csv_read_writer.write_timeseries(input_timeseries, output_path)
    output_timeseries = csv_read_writer.read_timeseries(output_path)

    assert input_timeseries == output_timeseries


def test_raster_segmenter():
    # Path
    input_path = get_filepath(test_folder, 'orthofoto_50cm.tif')


def test_tif_writer():
    input_path = get_filepath(test_folder, 'gelaendeschummerung.tif')
    output_path = get_filepath(test_folder, 'gelaendeschummerung_written.tif')

    input_dataset = gdal.Open(input_path)
    input_data = np.array(input_dataset.GetRasterBand(1).ReadAsArray())
    input_tif_info = TifInfo(input_path)

    TifWriter().write_tif(data=input_data, output_path=output_path, tif_info=input_tif_info)
    output_tif_info = TifInfo(output_path)
    assert input_tif_info == output_tif_info