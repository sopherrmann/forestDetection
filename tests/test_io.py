from forestdection.io import CsvReaderWriter
from forestdection.domain import Timeseries
from forestdection.filepath import FilepathProvider, get_filepath


def test_csv_read_write():
    # Paths
    test_folder = FilepathProvider().get_test_folder()
    output_path = get_filepath(test_folder, 'csv_read_write.csv')

    # timeseries
    dates = ['201901', '201902', '201801', '201807']
    sig0 = [12345, 3452, 12345, 9875]
    input_timeseries = Timeseries(dates, sig0)

    csv_read_writer = CsvReaderWriter()
    csv_read_writer.write_timeseries(input_timeseries, output_path)
    output_timeseries = csv_read_writer.read_timeseries(output_path)

    assert input_timeseries == output_timeseries
