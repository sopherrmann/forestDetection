from typing import List

import numpy

from forestdection.filepath import FilepathProvider
from forestdection.io2 import TifReaderWriter
from forestdection.main import Main
from forestdection.domain import Timeseries, TifInfo


class MockedTiffWriter(TifReaderWriter):
    def write_tif(self, data: numpy.array, output_path: str, tif_info: TifInfo):
        print(data)


class MockedMain(Main):
    def get_all_reference_timeseries(self, build: bool = False, plot: bool = False) -> List[Timeseries]:
        return [Timeseries(['2019-01', '2019-02', '2019-03'], [254./255, 253./255, 255./255], 'broadleaf', 'VH'),
                Timeseries(['2019-01', '2019-02', '2019-03'], [252./255, 251./255, 253./255], 'broadleaf', 'VV'),
                Timeseries(['2019-01', '2019-02', '2019-03'], [0./255, 1./255, 5./255], 'coniferous', 'VH'),
                Timeseries(['2019-01', '2019-02', '2019-03'], [2./255, 3./255, 4./255], 'coniferous', 'VV'),
                ]

    def _get_tif_info(self, _):
        return None


def test_complete():
    FilepathProvider.base_folder = '/home/sophie/repos/forestDetection/tests/mocks/generated'

    print("Starting")
    m = MockedMain()
    m.tif_reader_writer = MockedTiffWriter()
    rmsd = m.get_classified()
    a = 1
