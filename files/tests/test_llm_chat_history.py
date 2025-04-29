from pytest_bdd import scenarios, given, when, then, parsers
import pytest
import utils.rag_llm_utils as rag_llm_utils  # Update import if needed

scenarios("features/llm_chat_history.feature")

@pytest.fixture
def context():
    return {}

@given(parsers.parse('I have created a chat history of size {size:d}'))
def create_chat_history(context, size):
    context["chat_history"] = rag_llm_utils.init(ch=rag_llm_utils.ChatHistory(size=size))

@given(parsers.parse('I have set the prompt to "{prompt}"'))
def set_prompt(context, prompt):
    context["prompt"] = prompt

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

@when("I ask the prompt using rag_llm_utils with history")
def ask_prompt_with_history(context):
    llm_response, llm_response_index = rag_llm_utils.ask_prompt(
        context["prompt"],
        context["llm_user"],
        context["current_mp"],
        context["current_mp_constituency"],
    )
    context["llm_response"] = llm_response
    context["llm_response_index"] = llm_response_index

@then(parsers.parse('the last chat history user message should be "{expected_message}"'))
def check_last_history(context, expected_message):
    last_message = context["chat_history"].get_author_messages("Human")[-1]
    # If messages are objects (like HumanMessage), use .content
    try:
        last_message_text = last_message.content
    except AttributeError:
        last_message_text = last_message
    assert last_message_text == expected_message, f"Expected last message '{expected_message}', got '{last_message_text}'"