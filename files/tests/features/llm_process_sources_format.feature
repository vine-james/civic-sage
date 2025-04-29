Feature: Process source URLs in text into badge format

  Scenario: Input text contains SOURCE URL
    Given the source input text is "Check this link [SOURCE URL: https://google.com]"
    When I process the source text
    Then the processed source_text should contain ":violet-badge[:material/document_search:"

  Scenario: Input text without SOURCE URL
    Given the source input text is "There are no links here"
    When I process the source text
    Then the processed source_text should not contain ":violet-badge[:material/document_search:"