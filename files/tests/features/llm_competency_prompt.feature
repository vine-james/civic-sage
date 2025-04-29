Feature: User competency understanding
  As a user
  I want the LLM to respect my stated competencies
  So that the responses reflect my knowledge level.

  Scenario: LLM validates user competency bottom threshold
    Given I have set the competency to "Nothing at all"
    And I have set the prompt to "What was the exact textual rating I provided for my competency of UK politics?"
    And I have set the current_mp as "Paul Holmes"
    And I have set the current_mp_constituency as "Hamble Valley"
    When I ask the prompt using rag_llm_utils
    Then the answer should contain the text "Nothing at all"

  Scenario: LLM validates user competency top threshold
    Given I have set the competency to "A great deal"
    And I have set the prompt to "What was the exact textual rating I provided for my competency of UK government?"
    And I have set the current_mp as "Paul Holmes"
    And I have set the current_mp_constituency as "Hamble Valley"
    When I ask the prompt using rag_llm_utils
    Then the answer should contain the text "A great deal"