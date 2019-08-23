from robotlibcore import DynamicCore, keyword
from robot.errors import DataError
from robot.utils import timestr_to_secs, secs_to_timestr
from timeit import default_timer as timer

__version__ = '0.0.1'


def timestr_to_millisecs(timestr):
    return int(timestr_to_secs(timestr) * 1000)


def ms_to_s(ms):
    return ms / 1000.0


def _is_within_range(difference, lower_than, higher_than):
    return difference <= lower_than and difference >= higher_than


def timer_done(timer):
    return None not in [timer['start'], timer['stop'], timer['lower_than']]


def assert_string(benchmark_name, difference, lower_than, higher_than):
    difference = secs_to_timestr(ms_to_s(difference))
    lower_than = secs_to_timestr(ms_to_s(lower_than))
    higher_than = secs_to_timestr(ms_to_s(higher_than))
    return 'Difference ({}) in ”{}" is not in between {} and {}'.format(difference, benchmark_name, lower_than, higher_than)


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
        higher = 0
        lower = None
        # TODO: Maybe issue a warning when overwriting existing timers ?
        if benchmark_name in self.benchmarks:
            self.benchmarks[benchmark_name]['start'] =  timer()
            self.benchmarks[benchmark_name]['stop'] =  0
        else:
            self.benchmarks[benchmark_name] = {'start': timer(), 'stop': None, 'lower_than': None, 'higher_than': 0}

    @keyword
    def stop_timer(self, benchmark_name='default'):
        """
        """
        if benchmark_name not in self.benchmarks:
            raise DataError('Benchmark "%s" not started.' % benchmark_name)
        self.benchmarks[benchmark_name]['stop'] = timer()

    @keyword
    def configure_timer(self, lower_than, higher_than, benchmark_name='default'):
        if benchmark_name not in self.benchmarks:
            self.benchmarks[benchmark_name] = {'start': None, 'stop': None, 'lower_than': None, 'higher_than': 0}

        self.benchmarks[benchmark_name]['lower_than'] = timestr_to_millisecs(lower_than)
        self.benchmarks[benchmark_name]['higher_than'] = timestr_to_millisecs(higher_than)

    @keyword
    def verify_all_timers(self):
        failures = []
        for item in filter(lambda timer: timer_done(timer[1]), self.benchmarks.items()):
            benchmark_name = item[0]
            benchmark_data = item[1]
            difference = int((benchmark_data['stop'] - benchmark_data['start']) * 1000)
            lower_than = benchmark_data['lower_than']
            higher_than = benchmark_data['higher_than']
            if not _is_within_range(difference, lower_than, higher_than):
                failures.append(assert_string(benchmark_name, difference, lower_than, higher_than))
        if failures:
            raise AssertionError("\n".join(failures))

        return True

    @keyword
    def verify_single_timer(self, lower_than, higher_than=0, benchmark_name='default'):
        """
        """
        if benchmark_name not in self.benchmarks:
            raise DataError('Benchmark "%s" not started.' % benchmark_name)
        benchmark_data = self.benchmarks[benchmark_name]
        if not benchmark_data['stop']:
            raise DataError('Benchmark "%s" not finished.' % benchmark_name)

        difference = int((benchmark_data['stop'] - benchmark_data['start']) * 1000)
        lower_than = timestr_to_millisecs(lower_than)
        higher_than = timestr_to_millisecs(higher_than)
        if not _is_within_range(difference, lower_than, higher_than):
            raise AssertionError(assert_string(benchmark_name, difference, lower_than, higher_than))
        return True
