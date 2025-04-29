Feature: Chat history tracking
  As a user of the LLM wrapper
  I want my messages to be correctly stored in the chat history
  So that conversation context is preserved.

  Scenario: Prompt appears as the last user history message
    Given I have created a chat history of size 5
    And I have set the prompt to "What is the weather today?"
    And I have set the user as "test_user"
    And I have set the current_mp as "Paul Holmes"
    And I have set the current_mp_constituency as "Hamble Valley"
    When I ask the prompt using rag_llm_utils with history
    Then the last chat history user message should be "What is the weather today?"