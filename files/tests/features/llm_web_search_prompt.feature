Feature: Web Search Prompt
  As a user of the LLM wrapper
  I want to submit a prompt that triggers a web search
  So that I can ensure the LLM responds with a web search flag.

  Scenario: Ask unknown question receive web search flag
    Given I have set the prompt to "Whats the latest on Donald Trump?"
    And I have set the user as "test_user"
    And I have set the current_mp as "Paul Holmes"
    And I have set the current_mp_constituency as "Hamble Valley"
    When I ask the prompt using rag_llm_utils
    Then the answer should contain the text "WEB SEARCH:"