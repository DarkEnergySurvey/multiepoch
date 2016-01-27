'''tzinfo timezone information for SystemV/CST6.'''
from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as d
from pytz.tzinfo import memorized_ttinfo as i

class CST6(DstTzInfo):
    '''SystemV/CST6 timezone definition. See datetime.tzinfo for details'''

    _zone = 'SystemV/CST6'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1905,9,1,6,58,36),
d(1918,4,14,9,0,0),
d(1918,10,31,8,0,0),
d(1930,5,4,7,0,0),
d(1930,10,5,6,0,0),
d(1931,5,3,7,0,0),
d(1931,10,4,6,0,0),
d(1932,5,1,7,0,0),
d(1932,10,2,6,0,0),
d(1933,5,7,7,0,0),
d(1933,10,1,6,0,0),
d(1934,5,6,7,0,0),
d(1934,10,7,6,0,0),
d(1937,4,11,7,0,0),
d(1937,10,10,6,0,0),
d(1938,4,10,7,0,0),
d(1938,10,2,6,0,0),
d(1939,4,9,7,0,0),
d(1939,10,8,6,0,0),
d(1940,4,14,7,0,0),
d(1940,10,13,6,0,0),
d(1941,4,13,7,0,0),
d(1941,10,12,6,0,0),
d(1942,2,9,9,0,0),
d(1945,8,14,23,0,0),
d(1945,9,30,8,0,0),
d(1946,4,14,9,0,0),
d(1946,10,13,8,0,0),
d(1947,4,27,9,0,0),
d(1947,9,28,8,0,0),
d(1948,4,25,9,0,0),
d(1948,9,26,8,0,0),
d(1949,4,24,9,0,0),
d(1949,9,25,8,0,0),
d(1950,4,30,9,0,0),
d(1950,9,24,8,0,0),
d(1951,4,29,9,0,0),
d(1951,9,30,8,0,0),
d(1952,4,27,9,0,0),
d(1952,9,28,8,0,0),
d(1953,4,26,9,0,0),
d(1953,9,27,8,0,0),
d(1954,4,25,9,0,0),
d(1954,9,26,8,0,0),
d(1955,4,24,9,0,0),
d(1955,9,25,8,0,0),
d(1956,4,29,9,0,0),
d(1956,9,30,8,0,0),
d(1957,4,28,9,0,0),
d(1957,9,29,8,0,0),
d(1959,4,26,9,0,0),
d(1959,10,25,8,0,0),
d(1960,4,24,9,0,0),
        ]

    _transition_info = [
i(-25140,0,'LMT'),
i(-25200,0,'MST'),
i(-21600,3600,'MDT'),
i(-25200,0,'MST'),
i(-21600,3600,'MDT'),
i(-25200,0,'MST'),
i(-21600,3600,'MDT'),
i(-25200,0,'MST'),
i(-21600,3600,'MDT'),
i(-25200,0,'MST'),
i(-21600,3600,'MDT'),
i(-25200,0,'MST'),
i(-21600,3600,'MDT'),
i(-25200,0,'MST'),
i(-21600,3600,'MDT'),
i(-25200,0,'MST'),
i(-21600,3600,'MDT'),
i(-25200,0,'MST'),
i(-21600,3600,'MDT'),
i(-25200,0,'MST'),
i(-21600,3600,'MDT'),
i(-25200,0,'MST'),
i(-21600,3600,'MDT'),
i(-25200,0,'MST'),
i(-21600,3600,'MWT'),
i(-21600,3600,'MPT'),
i(-25200,0,'MST'),
i(-21600,3600,'MDT'),
i(-25200,0,'MST'),
i(-21600,3600,'MDT'),
i(-25200,0,'MST'),
i(-21600,3600,'MDT'),
i(-25200,0,'MST'),
i(-21600,3600,'MDT'),
i(-25200,0,'MST'),
i(-21600,3600,'MDT'),
i(-25200,0,'MST'),
i(-21600,3600,'MDT'),
i(-25200,0,'MST'),
i(-21600,3600,'MDT'),
i(-25200,0,'MST'),
i(-21600,3600,'MDT'),
i(-25200,0,'MST'),
i(-21600,3600,'MDT'),
i(-25200,0,'MST'),
i(-21600,3600,'MDT'),
i(-25200,0,'MST'),
i(-21600,3600,'MDT'),
i(-25200,0,'MST'),
i(-21600,3600,'MDT'),
i(-25200,0,'MST'),
i(-21600,3600,'MDT'),
i(-25200,0,'MST'),
i(-21600,0,'CST'),
        ]

CST6 = CST6()
