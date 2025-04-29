Feature: Source URL Prompt
  As a user of the LLM wrapper
  I want to submit a prompt and receive an answer containing source URLs
  So that I can verify references are included in responses.

  Scenario: Prompt response contains source URLs
    Given I have set the prompt to "Please provide sources for Paul Holmes latest election."
    And I have set the user as "test_user"
    And I have set the current_mp as "Paul Holmes"
    And I have set the current_mp_constituency as "Hamble Valley"
    When I ask the prompt using rag_llm_utils
    Then the answer should contain the text "SOURCE URL:"