from pytest_bdd import scenarios, given, when, then, parsers
import pytest
import utils.streamlit_utils as streamlit_utils

scenarios("features/get_mp_summary.feature")

@pytest.fixture
def context():
    return {}

@given(parsers.parse('the MP name is "{mp_name}"'))
def set_mp_name(context, mp_name):
    context["mp_name"] = mp_name

@when("I fetch the MP summary from the database")
def fetch_mp_summary(context):
    result = streamlit_utils.get_mp_summary_from_db(context["mp_name"])
    context["result"] = result

@then("the result should be a dictionary")
def check_result_dict(context):
    assert isinstance(context["result"], dict), f"Expected dict, got {type(context['result'])}: {context['result']}"

@then(parsers.parse('the result should be "{expected}"'))
def check_result_value(context, expected):
    assert context["result"] == expected, f"Expected '{expected}', got '{context['result']}'"