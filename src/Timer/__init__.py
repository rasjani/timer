from robotlibcore import DynamicCore, keyword
from robot.errors import DataError
from robot.utils import timestr_to_secs, secs_to_timestr
from robot.api import logger
from timeit import default_timer as timer

__version__ = '0.0.1'


def html_row(status, benchmark_name, lower_than, difference, higher_than):
    return '<tr class="{}"><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(status, benchmark_name, lower_than, difference, higher_than)

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
    """ Timer is small utility library that allows measuring the x amount of events within a single suite without the need to implement timing information into a separate scripts via robot.result api's.
    Library allows multiple timers to be ongoing at any time by providing a benchmark a name or just a single benchmark if no name is given.

    Each single timer can then be verified if its duration was within a given range or just lower than what was expected or all timers can be verified in one go if they where configured properly.
    """
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    ROBOT_LIBRARY_VERSION = __version__

    def __init__(self):
        self.benchmarks = {}
        DynamicCore.__init__(self, [])

    @keyword
    def start_timer(self, benchmark_name='default'):
        """
        Starts a single timer
        === Parameters ===
        ``benchmark_name`` Name of the benchmark, optional. Defaults to 'default'

        === Example: ===
        | Start Timer | mytimer |
        """
        # TODO: Maybe issue a warning when overwriting existing timers ?
        if benchmark_name in self.benchmarks:
            self.benchmarks[benchmark_name]['start'] = timer()
            self.benchmarks[benchmark_name]['stop'] = None
        else:
            self.benchmarks[benchmark_name] = {'start': timer(), 'stop': None, 'lower_than': None, 'higher_than': 0}

    @keyword
    def stop_timer(self, benchmark_name='default'):
        """
        Stops a single timer
        === Parameters ===
        ``benchmark_name`` Name of the benchmark, optional. Defaults to 'default'

        === Example: ===
        | Stop Timer | mytimer |
        """
        if benchmark_name not in self.benchmarks:
            raise DataError('Benchmark "%s" not started.' % benchmark_name)
        self.benchmarks[benchmark_name]['stop'] = timer()

    @keyword
    def configure_timer(self, lower_than, higher_than=0, benchmark_name='default'):
        """
        Configures/creates a single timer so that it can be verified later on.
        === Parameters ===
        ``lower_than`` Timestr value to check if the timer's total execution time is lower than.
        ``higher_than`` Timestr value to check if the timer's minimum value is higher than this, optional. Defaults to '0'
        ``benchmark_name`` Name of the benchmark, optional. Defaults to 'default'

        === Example: ===
        This will create a timer by name "anothertimer" that can then be checked that it lasted at least 5 seconds but not more than 10.
        | Configure Timer   | 10 seconds | 5 seconds | anothertimer |

        """
        if benchmark_name not in self.benchmarks:
            self.benchmarks[benchmark_name] = {'start': None, 'stop': None, 'lower_than': None, 'higher_than': 0}

        self.benchmarks[benchmark_name]['lower_than'] = timestr_to_millisecs(lower_than)
        self.benchmarks[benchmark_name]['higher_than'] = timestr_to_millisecs(higher_than)

    @keyword
    def verify_all_timers(self, fail=True):
        """
        Verifies all timers within a testsuite. Timer's must be done, eg `Start Timer` and `Stop Timer` keywords must have been called for it and it has to have been configured with `Configure Timer` keyword and lower_than parameter.
        Keyword will also write a html table into the logs that shows all finished timers and their status.
        === Parameters ===
        ``fail`` Should we throw an error if any timers are not within given ranges. Defaults to True
        === Example: ===
        | Verify All Timers |
        """
        failures = []
        html = ["<table><tr><th>Timer</th><th>Lower than</th><th>Execution Time</th><th>Higher Than</th></tr>"]
        for item in filter(lambda timer: timer_done(timer[1]), self.benchmarks.items()):
            benchmark_name = item[0]
            benchmark_data = item[1]
            difference = int((benchmark_data['stop'] - benchmark_data['start']) * 1000)
            lower_than = benchmark_data['lower_than']
            higher_than = benchmark_data['higher_than']
            if not _is_within_range(difference, lower_than, higher_than):
                html.append(html_row("fail", benchmark_name, lower_than, difference, higher_than))
                failures.append(assert_string(benchmark_name, difference, lower_than, higher_than))
            else:
                html.append(html_row("pass", benchmark_name, lower_than, difference, higher_than))

        html.append("</table")
        logger.info("".join(html), html=True)
        if fail and failures:
            raise AssertionError("\n".join(failures))

        if failures:
            return False

        return True

    @keyword
    def verify_single_timer(self, lower_than, higher_than=0, benchmark_name='default'):
        """
        Verifies a single timer.
        === Parameters ===
        ``lower_than`` Timestr value to check if the timer's total execution time is lower than.
        ``higher_than`` Timestr value to check if the timer's minimum value is higher than this, optional. Defaults to '0'
        ``benchmark_name`` Name of the benchmark, optional. Defaults to 'default'
        === Example ===
        | Start Timer           | yetananother |
        | Sleep                 | 3 Seconds    |
        | Stop Timer            | yetananother |
        | Verify Single Timer   | 4 Seconds    | benchmarkname=yetananother |

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
