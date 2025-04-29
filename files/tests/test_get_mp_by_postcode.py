from pytest_bdd import scenarios, given, when, then, parsers
import pytest
import utils.location_utils as location_utils

scenarios("features/get_mp_by_postcode.feature")

@pytest.fixture
def context():
    return {}

@given(parsers.parse("I have set my postcode to {postcode}"))
def set_coords(context, postcode):
    context["postcode"] = postcode

@when("I request the MP and constituency for that postcode")
def get_results(context):
    flag, constituency, mp = location_utils.get_mp_by_postcode(context["postcode"])
    context["result"] = {
        "flag": flag,
        "constituency": constituency,
        "mp": mp
    }

@then(parsers.parse('the constituency should be "{expected_constituency}"'))
def check_constituency(context, expected_constituency):
    assert context["result"]["constituency"] == expected_constituency

@then(parsers.parse('the MP should be "{expected_mp}"'))
def check_mp(context, expected_mp):
    assert context["result"]["mp"] == expected_mp

@then(parsers.parse('the flag should be "{expected_flag}"'))
def check_mp(context, expected_flag):
    assert context["result"]["flag"] == expected_flag