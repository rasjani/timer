from robotlibcore import DynamicCore, keyword
from robot.errors import DataError
from robot.utils import timestr_to_secs, secs_to_timestr
from timeit import default_timer as timer

__version__ = '0.0.1'


class Timer(DynamicCore):
    """
    """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = __version__

    def __init__(self):
        self.benchmarks = {}
        DynamicCore.__init__(self, [])

    @keyword
    def start_timer(self, benchmark_name='default'):
        """
        """
        # TODO: Maybe issue a warning when overwriting existing timers ?
        self.benchmarks[benchmark_name] = {'start': timer(), 'stop': None, 'lower_than': None, 'higher_than': 0}

    @keyword
    def stop_timer(self, benchmark_name='default'):
        """
        """
        if benchmark_name not in self.benchmarks:
            raise DataError('Benchmark "%s" not started.' % benchmark_name)
        self.benchmarks[benchmark_name]['stop'] = timer()

    @keyword
    def timer_results_within(self, lower_than, higher_than=0, benchmark_name='default'):
        """
        """
        if benchmark_name not in self.benchmarks:
            raise DataError('Benchmark "%s" not started.' % benchmark_name)
        benchmark_data = self.benchmarks[benchmark_name]
        if not benchmark_data['stop']:
            raise DataError('Benchmark "%s" not finished.' % benchmark_name)

        difference = int((benchmark_data['stop'] - benchmark_data['start']) * 1000)
        lower_than = int(timestr_to_secs(lower_than) * 1000)
        higher_than = int(timestr_to_secs(higher_than) * 1000)
        if not difference <= lower_than and difference >= higher_than:
            difference = secs_to_timestr(difference / 1000)
            lower_than = secs_to_timestr(lower_than / 1000)
            higher_than = secs_to_timestr(higher_than / 1000)
            raise AssertionError("Difference ({}) is not in between {} and {}".format(difference, lower_than, higher_than))
        return True
