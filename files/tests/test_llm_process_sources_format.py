from pytest_bdd import scenarios, given, when, then, parsers
import pytest
import utils.streamlit_utils as streamlit_utils

scenarios("features/llm_process_sources_format.feature")

@pytest.fixture
def context():
    return {}

@given(parsers.parse('the source input text is "{input_text}"'))
def given_source_input(context, input_text):
    context["input_text"] = input_text

@when("I process the source text")
def process_source_text(context):
    output_text, source_text = streamlit_utils.process_source_text(context["input_text"])
    context["processed"] = {
        "output_text": output_text,
        "source_text": source_text
    }

@then(parsers.parse('the processed source_text should contain "{expected}"'))
def source_text_should_contain(context, expected):
    assert expected in context["processed"]["output_text"] or expected in context["processed"]["source_text"], \
        f'Expected "{expected}" in processed texts.'

@then(parsers.parse('the processed source_text should not contain "{not_expected}"'))
def source_text_should_not_contain(context, not_expected):
    assert not_expected not in context["processed"]["output_text"] and not_expected not in context["processed"]["source_text"], \
        f'Did not expect "{not_expected}" in processed texts.'