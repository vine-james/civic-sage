import pytest
from pytest_bdd import scenarios, given, when, then, parsers

import utils.streamlit_utils as streamlit_utils

scenarios("features/get_mp_keywords.feature")

@pytest.fixture
def context():
    return {}

@given(parsers.parse('I have set the MP name as "{name}"'))
def mp_name(context, name):
    context["mp_name"] = name

@when("I get their keywords")
def get_keywords(context):
    context["result"] = streamlit_utils.get_mps_keywords(context["mp_name"])

@then(parsers.parse('the output should contain the text "{phrase}"'))
def output_contains(context, phrase):
    assert phrase in context["result"], f'Expected output to contain {phrase}, but got: {context["result"]}'