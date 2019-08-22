from robotlibcore import DynamicCore
from robot.api.deco import keyword
from robot.errors import DataError
from timeit import default_timer as timer

__version__ = '0.0.1'

class Timer(DynamicCore):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = __version__

    def __init__(self):
        self.benchmarks = {}

    @keyword
    def start_timer(self, benchmark_name = 'default'):
        self.benchmarks[benchmark_name] = {'start': timer(), 'end': None}


    @keyword
    def end_timer(self, benchmark_name = 'default'):
        if benchmark_name not in self.benchmarks:
            raise DataError('Benchmark "%s" not started.' % benchmark_name)
        self.benchmarks[benchmark_name]['end'] = timer()


