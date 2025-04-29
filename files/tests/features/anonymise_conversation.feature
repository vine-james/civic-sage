Feature: Anonymise sensitive information from text

  Scenario: Check regular text not anonymised
    Given the input text is "I had a bad day today"
    When I anonymise the text
    Then the output should not contain "<"

  Scenario: Check name anonymisation
    Given the input text is "My name is John Doe"
    When I anonymise the text
    Then the output should contain "<PERSON>"

  Scenario: Check omit tag <LOCATION> works
    Given the input text is "My current location is Bournemouth"
    When I anonymise the text
    Then the output should contain "Bournemouth"

  Scenario: Check name anonymisation omits MP name
    Given the input text is "My name is Paul Holmes"
    When I anonymise the text
    Then the output should contain "Paul Holmes"