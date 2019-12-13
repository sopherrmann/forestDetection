from forestdection.domain import TifInfo
from forestdection.filepath import get_filepath, FilepathProvider

filepath_provider = FilepathProvider()
test_folder = filepath_provider.get_test_folder()


def test_tif_info():
    input_path = get_filepath(test_folder, 'gelaendeschummerung.tif')
    info = TifInfo(input_path)

    assert info.origin_x == -2.5
    assert info.origin_y == 350002.5
    assert info.size_x == 1002
    assert info.size_y == 1002
    assert info.pixel_width == 2.5
    assert info.pixel_height == -2.5  # how?
    assert info.wkt_projection.split('AUTHORITY')[-1].split('","')[-1][:5] == '31256'

