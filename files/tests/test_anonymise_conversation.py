from pytest_bdd import scenarios, given, when, then, parsers
import pytest
import utils.analysis_utils as analysis_utils

scenarios("features/anonymise_conversation.feature")

@pytest.fixture
def context():
    return {}

@given(parsers.parse('the input text is "{text}"'))
def input_text(context, text):
    context["input_text"] = text

@when("I anonymise the text")
def anonymize_text(context):
    context["anon_output"] = analysis_utils.anonymize_text(context["input_text"], mp_name="Paul Holmes")

@then(parsers.parse('the output should contain "{expected}"'))
def output_should_contain(context, expected):
    assert expected in context["anon_output"], f'Expected "{expected}" to be in "{context["anon_output"]}"'

@then(parsers.parse('the output should not contain "{not_expected}"'))
def output_should_not_contain(context, not_expected):
    assert not_expected not in context["anon_output"], f'Did not expect "{not_expected}" in "{context["anon_output"]}"'