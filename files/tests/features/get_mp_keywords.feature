Feature: Get top MP keywords for recommendations

  Scenario: Existing MP returns keywords
    Given I have set the MP name as "Paul Holmes"
    When I get their keywords
    Then the output should contain the text ","

  Scenario: Non-MP returns no keywords
   Given I have set the MP name as "John Doe"
    When I get their keywords
    Then the output should contain the text "No historical search terms found. You're the first!"