*** Settings ***
Library     Timer
*** Test Cases ***

Can Start Timer
  Start Timer

Can Stop Timer
    Stop Timer

Can Check The Results
    ${res}=    Verify Single Timer   5   0
    Should Be True    ${res}

Can Throw Error
  Start Timer  error
  Sleep   5 seconds
  Stop Timer    error
  Run Keyword And Expect Error    STARTS: Difference
  ...                             Verify Single Timer   3   0    error

