Feature: Find MP and constituency by postcode

  Scenario: Return correct MP from postcode lookup
    Given I have set my postcode to BH8 8GR
    When I request the MP and constituency for that postcode
    Then the flag should be "Success"
    Then the constituency should be "Bournemouth West"
    And the MP should be "Jessica Toale"

  Scenario: Return no MP from postcode lookup
    Given I have set my postcode to AAAA
    When I request the MP and constituency for that postcode
    Then the flag should be "Input does not match postcode format"