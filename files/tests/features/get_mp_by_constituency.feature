Feature: Find MP and constituency by location coordinates

  Scenario: Look up MP and constituency for Bournemouth West
    Given I have set my coordinates to 50.7435 latitude and -1.8983 longitude
    When I request the MP and constituency for those coordinates
    Then the constituency should be "Bournemouth West"
    And the MP should be "Jessica Toale"

  Scenario: Look up MP and constituency for Bournemouth West
    Given I have set my coordinates to 101.9758 latitude and -14.2105 longitude
    When I request the MP and constituency for those coordinates
    Then the constituency should be "Bournemouth West"
    And the MP should be "Jessica Toale"