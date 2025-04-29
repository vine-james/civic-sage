import requests
import utils.constants as constants

from streamlit_js_eval import get_geolocation

def get_location_by_streamlit():
    try:
        location = get_geolocation()

        if location is None:
            return None, None
        
        return location["coords"]["latitude"], location["coords"]["longitude"]
    
    except Exception as e:
        print(f"Geolocation package experienced an error: {e}")
        return None, None


def get_location_details(longitude, latitude):
    try:
        response_location = requests.get(f"https://api.postcodes.io/postcodes?lon={longitude}&lat={latitude}")

        if response_location.status_code == 200:
            data = response_location.json()
            
            if data["result"] == None:
                return "Location unavailable", "Location unavailable", "Location unavailable", "Location unavailable", "Location unavailable", "Location unavailable"

            admin_ward = data["result"][0]["admin_ward"]
            postcode = data["result"][0]["postcode"]
            constituency = data["result"][0]["parliamentary_constituency"]
            admin_ward_code = data["result"][0]["codes"]["admin_ward"]
            constituency_code = data["result"][0]["codes"]["parliamentary_constituency"]

            return "Success", admin_ward, postcode, constituency, admin_ward_code, constituency_code

    except Exception as e:
        print(f"Error getting location: {e}")


def get_mp_by_constituency(session_state):
    if not session_state["location"][0] or not session_state["location"][1]:
        return "Location unavailable", None, None, None, None

    flag, admin_ward, postcode, constituency, _, _ = get_location_details(session_state["location"][1], session_state["location"][0])

    if flag == "Location unavailable":
        return "Location unavailable", None, None, None, None

    # If get_mp, then function is for getting query for initial MP search
    try:
        response_mp = requests.get(f"https://www.theyworkforyou.com/api/getMP?key={constants.TOKEN_THEYWORKFORYOU}&constituency={constituency}&output=json")
        mp_name = None

        if response_mp.status_code == 200:
            data = response_mp.json()
            mp_name = data["full_name"]

        return "Success", admin_ward, postcode, constituency, mp_name

    except Exception as e:
        print(f"Error getting constituency: {e}")
        

def get_mp_by_postcode(postcode):
    response_mp_postcode = requests.get(f"https://www.theyworkforyou.com/api/getMP?key={constants.TOKEN_THEYWORKFORYOU}&postcode={postcode}&output=json")

    try:
        if response_mp_postcode.status_code == 200:
            data = response_mp_postcode.json()
            mp = data["full_name"]
            constituency = data["constituency"]

            return constituency, mp

    except Exception as e:
        print(f"Error getting postcode: {e}")
    