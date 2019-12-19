import numpy as np

from forestdection.service import IndicatorCalculation


def test_get_centered_std_timeseries():
    indicator_calculation = IndicatorCalculation()
    data = [1, 2, 3]
    std, centered = indicator_calculation.get_centered_std_timeseries(data)
    assert std == 1.0
    assert (centered == np.array([-1, 0, 1])).all()


def test_get_centered_std_cube():
    indicator_calculation = IndicatorCalculation()
    data = np.ones((10, 10, 3))
    data[:, :, 0] = 2
    std, centered = indicator_calculation.get_centered_std_cube(data)

    assert np.min(centered) == 1 - 4/3
    assert np.max(centered) == 2 - 4/3

    ref = np.sqrt(((2 - 4/3)**2 + (1 - 4/3)**2 * 2) / 2)
    assert std[0, 0] == ref
