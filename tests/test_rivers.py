import numpy as np
from tools.romsnc import river

TESTFILE = '/home/annks/river_test.nc'

def test_load_river_no_grid():
    r = river(TESTFILE)
    assert r.riverno.shape[0] > 0

def test_index_river():
    r = river(TESTFILE)

    # Test indexing with one int index
    r2 = r[0]
    print(r2.riverno)
    assert r2.riverno.shape == (1,)
    assert r2.riverno[0] == r.riverno[0]

    r2 = r[np.int64(0)]
    print(r2.riverno)
    assert r2.riverno.shape == (1,)
    assert r2.riverno[0] == r.riverno[0]

    # Test indexing with np.where
    r2 = r[np.where(r.riverno == 247)]
    I = np.argmin(abs(r.riverno - 247))
    assert r2.riverno.shape == (1,)
    assert r2.riverno[0] == r.riverno[I]
