from pytest_bdd import scenarios, given, when, then, parsers
import pytest
import utils.rag_llm_utils as rag_llm_utils

scenarios("features/llm_memory_summary.feature")

@pytest.fixture
def context():
    return {}

@given(parsers.parse('I have created a chat history of size {size:d}'))
def create_chat_history(context, size):
    print("Setting up history")
    context["chat_history"] = rag_llm_utils.init(ch=rag_llm_utils.ChatHistory(size=size))

@given(parsers.parse('I have set the user as "{llm_user}"'))
def set_user(context, llm_user):
    context["llm_user"] = rag_llm_utils.User(competencies={
        "UK Politics": "Nothing at all",
        "UK Parliament": "Nothing at all",
        "UK Government": "Nothing at all",
    })

@given(parsers.parse('I have set the current_mp as "{current_mp}"'))
def set_current_mp(context, current_mp):
    context["current_mp"] = current_mp

@given(parsers.parse('I have set the current_mp_constituency as "{constituency}"'))
def set_constituency(context, constituency):
    context["current_mp_constituency"] = constituency

@when(parsers.parse('I ask the prompt "{prompt}" using rag_llm_utils with history'))
def ask_prompt(context, prompt):
    llm_response, llm_response_index = rag_llm_utils.ask_prompt(
        prompt,
        context["llm_user"],
        context["current_mp"],
        context["current_mp_constituency"],
    )
    context["llm_response"] = llm_response
    context["llm_response_index"] = llm_response_index


@then(parsers.parse('the answer should contain the text "{expected_text}"'))
def check_response_contains(context, expected_text):
    assert expected_text in context["llm_response"], f"Expected '{expected_text}' in '{context['llm_response']}'"