from pytest_bdd import scenarios, given, when, then, parsers
import pytest
import utils.rag_llm_utils as rag_llm_utils  # Adjust path if needed

scenarios("features/llm_competency_prompt.feature")

@pytest.fixture
def context():
    return {}

@given(parsers.parse('I have set the competency to "{competency}"'))
def set_user_competency(context, competency):
    context["llm_user"] = rag_llm_utils.User(competencies={
        "UK Politics": competency,
        "UK Parliament": competency,
        "UK Government": competency,
    })

@given(parsers.parse('I have set the prompt to "{prompt}"'))
def set_prompt(context, prompt):
    context["prompt"] = prompt

@given(parsers.parse('I have set the current_mp as "{current_mp}"'))
def set_current_mp(context, current_mp):
    context["current_mp"] = current_mp

@given(parsers.parse('I have set the current_mp_constituency as "{constituency}"'))
def set_constituency(context, constituency):
    context["current_mp_constituency"] = constituency

@when("I ask the prompt using rag_llm_utils")
def ask_prompt(context):
    llm_response, llm_response_index = rag_llm_utils.ask_prompt(
        context["prompt"],
        context["llm_user"],
        context["current_mp"],
        context["current_mp_constituency"],
    )
    context["llm_response"] = llm_response
    context["llm_response_index"] = llm_response_index

@then(parsers.parse('the answer should contain the text "{expected_text}"'))
def check_response(context, expected_text):
    assert expected_text in context["llm_response"], f"Expected '{expected_text}' in '{context['llm_response']}'"