import os


class FilenameProvider:

    def get_timeseries_name(self, polarization: str, forest_type: str):
        return f'{polarization}_{forest_type}'

    def get_info_from_name(self, name: str):
        return name.split('_')

    def append_sufix_to_tif(self, input_filename: str, output_sufix: str):
        return input_filename.replace('.tif', f'_{output_sufix}.tif')

    def get_timeseries_filename(self, polarization: str, forest_type: str):
        return f'timeseries_{polarization}_{forest_type}.csv'

    def get_rmsd_filename(self, polarization: str, forest_type: str):
        return f'rmsd_{polarization}_{forest_type}.tif'

    def get_pearson_filename(self, polarization: str, forest_type: str):
        return f'pearson_{polarization}_{forest_type}.tif'


class FilepathProvider:
    # TODO make this smarter (e.g.: config path)
    filename_provider = FilenameProvider()
    base_folder = '/home/sophie/Documents/data/forest_detection'

    def _get_and_make_folder(self, main, sub):
        path = os.path.join(self.base_folder, main, sub)
        if not os.path.isdir(path):
            os.mkdir(path)
        return path

    # main folders
    def _get_input_folder(self, name):
        return self._get_and_make_folder('input', name)

    def _get_result_folder(self, name):
        return self._get_and_make_folder('result', name)

    def _get_tmp_folder(self, name):
        return self._get_and_make_folder('tmp', name)

    # special purpose folders
    # input
    def get_sig0_mm_folder(self):
        return self._get_input_folder('sig0_monthly_mean')

    def get_shape_folder(self):
        return self._get_input_folder('reference_shape')

    def get_sentinel_hlr_folder(self):
        return self._get_input_folder('sentinel_hlr')

    # tmp
    def get_cropped_mm_folder(self):
        return self._get_tmp_folder('cropped_mm')

    def get_test_folder(self):
        return self._get_tmp_folder('test')

    def get_timeseries_folder(self):
        return self._get_tmp_folder('timeseries')

    def get_plot_folder(self):
        return self._get_tmp_folder('plot')

    # results
    def get_rmsd_folder(self):
        return self._get_result_folder('rmsd')

    def get_pearson_folder(self):
        return self._get_result_folder('pearson')

    # complete filepaths
    def get_cropped_mm_file(self, input_filename, output_sufix):
        output_filename = self.filename_provider.append_sufix_to_tif(input_filename, output_sufix)
        return os.path.join(self.get_cropped_mm_folder(), output_filename)

    def get_timeseries_file(self, polarization: str, forest_type: str):
        folder = self.get_timeseries_folder()
        name = self.filename_provider.get_timeseries_filename(polarization, forest_type)
        return get_filepath(folder, name)

    def get_rmsd_file(self, polarization: str, forest_type: str):
        folder = self.get_rmsd_folder()
        name = self.filename_provider.get_rmsd_filename(polarization, forest_type)
        return get_filepath(folder, name)

    def get_pearson_file(self, polarization: str, forest_type: str):
        folder = self.get_pearson_folder()
        name = self.filename_provider.get_pearson_filename(polarization, forest_type)
        return get_filepath(folder, name)

    def get_by_polarisation_from_folder(self, folder):
        all_files = get_files_from_folder(folder)
        vv = []
        vh = []
        for f in all_files:
            part = os.path.basename(f).split('_')[3]
            if part.endswith('VV-'):
                vv.append(f)
            elif part.split('VH-'):
                vh.append(f)
        return {'VV': vv, 'VH': vh}

    def get_input_shape_files_by_forest_type(self):
        shape_folder = self.get_shape_folder()
        all_files = get_files_from_folder(shape_folder, '.shp')
        return {self.get_forest_type_from_shape_file(path): path for path in all_files}

    def get_forest_type_from_shape_file(self, shape_path: str):
        shape_name = os.path.basename(shape_path)
        return shape_name.split('.')[0]

    def get_input_mm_files_by_polarisation(self):
        orig_mm_folder = self.get_sig0_mm_folder()
        return self.get_by_polarisation_from_folder(orig_mm_folder)


def get_files_from_folder(folder: str, ext: str = None):
    files = []
    for f in os.listdir(folder):
        file_path = os.path.join(folder, f)
        if os.path.isfile(file_path) and (not ext or file_path.endswith(ext)):
            files.append(file_path)
    return files


def get_filename_from_path(filepath):
    return os.path.basename(filepath)


def get_filepath(folder_path, filename):
    return os.path.join(folder_path, filename)


def get_date_from_filename(filename: str) -> str:
    parts = filename.split('_')[0]
    return f'{parts[1:5]}-{parts[5:7]}'
