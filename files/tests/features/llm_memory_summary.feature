Feature: Remembering previous prompt
  As a user of the LLM wrapper
  I want to send multiple prompts and the LLM should remember previous context
  So that I can maintain a conversation.

  Scenario: Remember LLM conversation history
    Given I have created a chat history of size 5
    And I have set the user as "test_user"
    And I have set the current_mp as "Paul Holmes"
    And I have set the current_mp_constituency as "Hamble Valley"
    When I ask the prompt "What does Paul think about education?" using rag_llm_utils with history
    And I ask the prompt "What did we just talk about?" using rag_llm_utils with history
    Then the answer should contain the text "education"