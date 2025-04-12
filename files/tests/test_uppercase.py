from pytest_bdd import scenarios, given, when, then, parsers
import pytest
import utils.streamlit_utils as st_utils

# Load the feature
scenarios("features/uppercase.feature")
# Load the feature

@pytest.fixture
def context():
    """Shared context between steps."""
    return {}

@given(parsers.parse('I have entered the text "{text}"'))
def input_text(context, text):
    context["input_text"] = text
    return context["input_text"]

@when("the conversion function is called")
def call_conversion_function(context):
    context["result"] = st_utils.convert_to_uppercase(context["input_text"])
    return context["result"]

@then(parsers.parse('I should see the text "{expected_text}"'))
def validate_output(context, expected_text):
    assert context["result"] == expected_text