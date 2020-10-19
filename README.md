robotframework-timer
====================

Timer is small utility library that allows measuring the x amount of events within a single suite without the need to implement timing information into a separate scripts via robot.result api's.

Library allows multiple timers to be ongoing at any time by providing a benchmark a name or just a single benchmark if no name is given.

Each single timer can then be verified if its duration was within a given range or just lower than what was expected or all timers can be verified in one go if they where configured properly.


# Installation

`pip install robotframework-timer`

# Examples:

```robotframework
*** Settings ***
Library         Timer
Suite Teardown    Verify Benchmark
Test Setup      Benchmark Setup
Test Teardown   Benchmark TearDown

*** Keywords ***
Benchmark Setup
  Start Timer   ${TEST NAME}
Benchmark TearDown
  Stop Timer    ${TEST NAME}
  Verify Single Timer    3 seconds   0 seconds   ${TEST NAME}

*** Test Cases ***
Example No 1 Passes
  Sleep   1 second

Example No 2 Passes
  Sleep   2 second

Example No 3 Will Fail
  Sleep   3 second

Verify Benchmark
  Verify All Timers   fail_on_errors=False
```



