import numpy as np
from osgeo import gdal

from forestdection.domain import Timeseries, TifInfo, RasterCube
from forestdection.filepath import FilepathProvider, get_filepath
from forestdection.io2 import CsvReaderWriter, TifReaderWriter, RasterSegmenter

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
    input_path = get_filepath(test_folder, 'gelaendeschummerung.tif')
    input_dataset = gdal.Open(input_path)
    input_raster = np.array(input_dataset.GetRasterBand(1).ReadAsArray())

    # segment raster
    raster_segmenter = RasterSegmenter()
    cube = raster_segmenter.get_next_cube([input_path])
    cubes = []
    while cube:
        cubes.append(cube)
        cube = raster_segmenter.get_next_cube([input_path])

    # reduce cube dimension
    to_write_cubes = []
    for c in cubes:
        twc = RasterCube(c.col_off, c.row_off, c.data[:, :, 0])
        to_write_cubes.append(twc)

    # Get one raster of cubes
    output_raster = raster_segmenter.get_raster_from_cubes(to_write_cubes)

    assert not np.argwhere(np.isnan(output_raster))
    assert output_raster.shape == input_raster.shape
    assert (output_raster == input_raster).all()


def test_tif_writer():
    input_path = get_filepath(test_folder, 'gelaendeschummerung.tif')
    output_path = get_filepath(test_folder, 'gelaendeschummerung_written.tif')

    input_dataset = gdal.Open(input_path)
    input_data = np.array(input_dataset.GetRasterBand(1).ReadAsArray())
    input_tif_info = TifInfo(input_path)

    TifReaderWriter().write_tif(data=input_data, output_path=output_path, tif_info=input_tif_info)
    output_tif_info = TifInfo(output_path)
    assert input_tif_info == output_tif_info
