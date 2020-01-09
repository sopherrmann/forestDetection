from typing import List

import numpy as np
from osgeo import gdal


class Timeseries:

    def __init__(self, dates: List[str] = None, sig0s: List[float] = None, forest_type: str = None, polarization: str = None):
        self.forest_type = forest_type
        self.polarization = polarization
        self.dates = dates if dates is not None else []
        self.sig0s = sig0s if sig0s is not None else []

    def push(self, date, sig0):
        self.dates.append(date)
        self.sig0s.append(float(sig0))  # Sig0 are stored as signed sixteen bit integers > if factor 100 is removed float

    def push_all(self, dates: List[str], sig0s: List[int]):
        self.dates += dates
        self.sig0s += sig0s

    def set_description(self, forest_type: str = None, polarization: str = None):
        self.forest_type = forest_type
        self.polarization = polarization

    def get_description(self):
        return f'{self.polarization}_{self.forest_type}'

    def get_zip(self):
        return zip(self.dates, self.sig0s)

    def get_attributes(self):
        return ['date', 'sig0']

    def get_sorted(self):
        sorted_ts = [(d, s) for d, s in sorted(self.get_zip())]
        return zip(*sorted_ts)

    def get_size(self):
        return len(self.dates)

    def __eq__(self, other):
        dates_check = self.dates == other.dates
        sig0_check = self.sig0s == other.sig0s
        return dates_check and sig0_check


class RasterCube:

    def __init__(self, col_off: int, row_off: int, data: np.array):
        self.col_off = col_off
        self.row_off = row_off
        self.data = data

    def get_extend(self):
        col_max = self.col_off + self.data.shape[1]
        row_max = self.row_off + self.data.shape[0]
        return self.col_off, col_max, self.row_off, row_max


class TifInfo:

    def __init__(self, path: str):
        dataset = gdal.Open(path)

        transform = dataset.GetGeoTransform()
        self.origin_x = transform[0]
        self.origin_y = transform[3]
        self.pixel_width = transform[1]
        self.pixel_height = transform[5]

        self.wkt_projection = dataset.GetProjectionRef()

        self.size_x = dataset.RasterXSize
        self.size_y = dataset.RasterYSize

    def __eq__(self, other):
        return self.origin_x == other.origin_x and self.origin_y == other.origin_y \
               and self.pixel_width == other.pixel_width and self.pixel_height == other.pixel_height \
               and self.wkt_projection == other.wkt_projection \
               and self.size_x == other.size_x and self.size_y == other.size_y


class Indicators:

    def __init__(self):
        self.forest_types = []
        self.polarizations = []
        self.types = []
        self.data = []

    def push(self, forest_type: str, polarization: str, type_: str, data: np.array):
        self.forest_types.append(forest_type)
        self.polarizations.append(polarization)
        self.types.append(type_)
        self.data.append(data)

    def push_all(self, forest_types: List[str], polarizations: List[str], types_: List[str], data: List[np.array]):
        self.forest_types += forest_types
        self.polarizations += polarizations
        self.types += types_
        self.data += data

    def get_data_by_description(self, forest_type: str = None, polarization: str = None, type_: str = None):
        indices = self.get_part_indices(forest_type, polarization, type_)
        data = [d for i, d in enumerate(self.data) if i in indices]
        return np.dstack(data)

    def get_part_indices(self, forest_type: str = None, polarization: str = None, type_: str = None):
        indices = set(range(0, len(self.forest_types)))

        if forest_type:
            indices = self._get_indices_set(self.forest_types, forest_type) & indices
        if polarization:
            indices = self._get_indices_set(self.polarizations, polarization) & indices
        if type_:
            indices = self._get_indices_set(self.types, type_)

        return indices

    def _get_indices_set(self, to_check: list, value) -> set:
        return {i for i, j in enumerate(to_check) if j == value}
