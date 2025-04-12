Feature: Uppercase conversion
  As a user of the Streamlit Uppercase Converter
  I want to input text and see it displayed in uppercase
  So that I can ensure the app correctly transforms the text.

  Scenario: Convert a lowercase string to uppercase
    Given I have entered the text "hello world"
    When the conversion function is called
    Then I should see the text "HELLO WORLD"