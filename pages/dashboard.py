import streamlit as st
import utils.streamlit_utils as st_utils
import utils.constants as constants
import pandas as pd

st_utils.create_page_setup(page_name="Dashboard")

def run():
    """
    Run the dashboard
    """

    st.write("https://blog.streamlit.io/streamlit-authenticator-part-1-adding-an-authentication-component-to-your-app/")


    st.write("First -> Log in to the 'MP side', which MP are we looking for? 2. Pull the data for that MP. 3. Show dashboard for data collected specific to that MP.")
    st.write("Charts, metrics, plus info reported as wrong by the users")
    

    for file in constants.PATH_CONVERSATIONS.iterdir():
        st.table(pd.read_csv(file))

    import time
    with st.status("Downloading data...", expanded=True) as status:
        st.write("Searching for data...")
        time.sleep(2)
        st.write("Found URL.")
        time.sleep(1)
        st.write("Downloading data...")
        time.sleep(1)
        status.update(
            label="Download complete!", state="complete", expanded=False
        )


@st.dialog("Login to the User Dashboard")
def login():
    password_input = st.text_input("Enter Password")
    if st.button("Submit"):
        if password_input == constants.PASSWORD_DASHBOARD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Password incorrect")


if "authenticated" not in st.session_state:
    login()

elif "authenticated" in st.session_state:
    if not st.session_state.authenticated:
        login()

    else:
        run()


