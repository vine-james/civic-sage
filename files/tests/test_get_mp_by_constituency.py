from pytest_bdd import scenarios, given, when, then, parsers
import pytest
import utils.location_utils as location_utils

scenarios("features/get_mp_by_constituency.feature")

@pytest.fixture
def context():
    return {}

@given(parsers.parse("I have set my coordinates to {lat:f} latitude and {lon:f} longitude"))
def set_coords(context, lat, lon):
    context["session_state"] = {
        "location": {
            "coords": {
                "latitude": lat,
                "longitude": lon
            }
        }
    }

@when("I request the MP and constituency for those coordinates")
def get_results(context):
    admin_ward, postcode, constituency, mp_name = location_utils.get_mp_by_constituency(context["session_state"])
    context["result"] = {
        "constituency": constituency,
        "mp": mp_name
    }

@then(parsers.parse('the constituency should be "{expected_constituency}"'))
def check_constituency(context, expected_constituency):
    assert context["result"]["constituency"] == expected_constituency

@then(parsers.parse('the MP should be "{expected_mp}"'))
def check_mp(context, expected_mp):
    assert context["result"]["mp"] == expected_mp