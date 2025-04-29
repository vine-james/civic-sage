Feature: Find MP and constituency by location coordinates

  Scenario: Return correct MP from constituency lookup
    Given I have set my coordinates to 50.7435 latitude and -1.8983 longitude
    When I request the MP and constituency for those coordinates
    Then the constituency should be "Bournemouth West"
    And the MP should be "Jessica Toale"

  Scenario: Return no MP from constituency lookup
    Given I have set my coordinates to 101.9758 latitude and -14.2105 longitude
    When I request the MP and constituency for those coordinates
    Then the constituency should be "None"
    And the MP should be "None"