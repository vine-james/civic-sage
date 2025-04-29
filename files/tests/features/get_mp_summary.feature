Feature: Get MP summary from database

  Scenario: MP summary returns for real MP
    Given the MP name is "Paul Holmes"
    When I fetch the MP summary from the database
    Then the result should be a dictionary

  Scenario: No MP summary returns for non-MP
    Given the MP name is "John Doe"
    When I fetch the MP summary from the database
    Then the result should be "No MP summary found"