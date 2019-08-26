*** Settings ***
Library         Timer
Test Setup      Benchmark Setup
Test Teardown   Benchmark TearDown

*** Keywords ***
Benchmark Setup
  Configure Timer   3 seconds   0 seconds   ${TEST NAME}
  Start Timer   ${TEST NAME}

Benchmark TearDown
  Stop Timer    ${TEST NAME}
  Verify Single Timer    3 seconds   0 seconds   ${TEST NAME}

*** Test Cases ***
Example No 1 Passes
  Sleep   1 second

Example No 2 Passes
  Sleep   2 second


Verify So Far
  [Setup]       No Operation
  [Teardown]    No Operation
  Verify all Timers

Example No 3 Will Fail
  [Teardown]    No Operation
  Sleep   3 second
  Stop Timer    ${TEST NAME}
  Run Keyword And Expect Error    STARTS: Difference
  ...                             Verify Single Timer   3   0    ${TEST NAME}

Final Verify Failure
  [Setup]       No Operation
  [Teardown]    No Operation
  Run Keyword And Expect Error    STARTS: Difference
  ...                             Verify All Timers

Final Verify Without Failing
  [Setup]       No Operation
  [Teardown]    No Operation
  Verify All Timers   False
