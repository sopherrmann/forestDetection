import os


class FilepathProvider:
    # TODO make this smarter (e.g.: config path)
    base_folder = '/path/to/base_dir'

    def _get_and_make_folder(self, main, sub):
        path = os.path.join(self.base_folder, main, sub)
        if not os.path.isdir(path):
            os.mkdir(path)
        return path

    def _get_input_folder(self, name):
        return self._get_and_make_folder('input', name)

    def _get_result_folder(self, name):
        return self._get_and_make_folder('result', name)

    def _get_tmp_folder(self, name):
        return self._get_and_make_folder('tmp', name)

    def get_sig0_mm_dir(self):
        return self._get_input_folder('sig0_monthly_means')

    def get_shape_folder(self):
        return self._get_input_folder('reference_shape')

    def get_cropped_mm_folder(self):
        return self._get_tmp_folder('cropped_mm')

    def get_cropped_mm_file(self, input_filename, output_sufix):
        output_filename = input_filename.replace('.tif', f'_{output_sufix}.tif')
        return os.path.join(self.get_cropped_mm_folder(), output_filename)

    def get_by_polarisation_from_folder(self, folder, forest_type=None):
        pass

    def get_reference_folder(self, reference_type):
        pass

    def get_result_folder(self, result_type):
        pass


def get_filename_from_path(filepath):
    return os.path.basename(filepath)
