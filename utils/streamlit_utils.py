import streamlit as st
import requests
from streamlit_theme import st_theme


import pandas as pd
from datetime import datetime

import utils.constants as constants

THEMES_MAIN = "#3087ff"

THEMES_SELECT_BACKGROUND = "#e3e7ee"
THEMES_SELECT_ELEMENT = "#1d2345"

"""


St.app_logo
st_extras.mentions (for ChatGPT mentions + in the text where we need it. )
Markdownlit if this is abit useless

 Add Vertical Space

Color streamlit headers - now native with stheader(divider=)

POTENTIALLY:


Chart container
style_metric_cards (if I want them to look abit fancier)
st.stateful chart -- Possibly if the regular ChatGPT integration isnt good enough/doesnt keep track of history
st.stylable_container - If I want more customisation of how it looks
st.tags - For a side-bar of chat history to show basic summary e.g. MP with color of party, any gov role acronyms






Loading system needed?
Especially for dashboard page



Chat message format:
[text here]

> [Sources: Information accurate to my databases as of DD-MM-YYYY] (expandable)

"""

def get_version() -> str:
        try:
            response = requests.get(
                url="https://api.github.com/repos/vine-james/civic-sage/releases/latest", 
                headers={"Authorization": f"Bearer {constants.TOKEN_GITHUB}"}, 
                timeout=10
            )

            if response.status_code == 200:
                return response.json().get("tag_name", "No version found")[1:]
            
            else:
                # TODO: Test case
                print(f"Error: Unable to fetch version (HTTP {response.status_code})")
                return "Unavailable"
            
        except Exception:
            # TODO: Test case
            print("Error: Unable to connect to GitHub")
            return "Unavailable"



def create_header_bar() -> None:
   st.markdown("""
        <style>
            [data-testid="stDecoration"] {
                background:""" + f"{THEMES_MAIN};" + """
                height: 12%;
            }
        </style>
        """, unsafe_allow_html=True) 


def get_themed_icon(file_path):
    # Adapt logo path to dark-mode variant dependent on theme mode set by user (minor QoL)
    # theme = st_theme()

    # # Check if the app is in "dark mode" or "light mode"
    # print(theme)
    # if theme["base"] == "dark":
    #     print(file_path.with_name(file_path.stem + "-white" + file_path.suffix))
    #     return file_path.with_name(file_path.stem + "-white" + file_path.suffix)
    
    return file_path


def create_sidebar() -> None:
     with st.sidebar:
        # Logo, Title, Version
        # st.image(constants.PATH_IMAGES / "civic-sage-logo-text.png", width=160)

        st.image(get_themed_icon(constants.PATH_IMAGES / "civic-sage-logo.png"), width=160)
        st.logo(constants.PATH_IMAGES / "none.png", icon_image=constants.PATH_IMAGES / "civic-sage-logo.png", size="large")

        st.markdown(
            f"""
            <p style='font-size:28px; margin-bottom: -10px; color: {THEMES_MAIN};'><b>Civic Sage</b></p>
            <p style='margin-bottom: 0px;'>Version {get_version()}</p>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        # Public Pages
        st.subheader("Navigate")
        st.page_link("streamlit_app.py", label="Home", icon=":material/home:")
        st.page_link("pages/search.py", label="Search for an MP", icon=":material/search:")
        st.page_link("pages/dashboard.py", label="Dashboard", icon=":material/view_kanban:")

        # st.subheader("🔒 Private")
        # st.page_link("pages/testing.py", label="[DEV] Testing")

        st.divider()

        # Dissertation review notice
        with st.expander("**Survey Feedback**", icon=":material/feedback:"):
            st.info("**REVIEWERS:** Are you testing this artefact as part of a requested survey? Access the [JISC Survey form here](https://app.onlinesurveys.jisc.ac.uk/s/bournemouth/dissertation-response-survey). This is the only acceptable way to provide feedback.")
            st.image(constants.PATH_IMAGES / "survey-qr-code.png")

        


def create_page_config(page_name: str) -> None:
    st.set_page_config(
        page_title=f"Civic Sage | {page_name}",
        page_icon="🗳️",
        layout="centered",
        initial_sidebar_state="expanded",
    )


def save_conversation_to_csv() -> None:
    # If a previous conversation (array of messages) existed, save it before resetting.
    if "messages" in st.session_state:
        # TODO: Find a better way than layered if conditions
        if len(st.session_state["messages"]) > 1: 
            previous_mp = st.session_state.current_selected_mp

            df_conversation = pd.DataFrame({
                "MP": [previous_mp] * len(st.session_state.messages),
                "Message Date": [message["date"] for message in st.session_state.messages],
                "Message Time": [message["time"] for message in st.session_state.messages],
                "Message Type": [message["role"] for message in st.session_state.messages],
                "Message Content": [message["message"]["content"] for message in st.session_state.messages],
            })
            df_conversation.to_csv(constants.PATH_CONVERSATIONS / f"{previous_mp.lower().replace(' ', '-')}_{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.csv", index=False)

            st.session_state.messages = []


def inject_html_styling() -> None:
    # Inject re-styling theme HTML/CSS
    st.markdown(
        """
        <style>

        /* Regular Button */
        .stButton > button { 
            background-color: """ + f"{THEMES_MAIN};" + """
            color: white; 
            transition: all .35s ease;
            border: none;
        }
        
        .stButton > button:hover {
            background-color: """ + f"{THEMES_SELECT_BACKGROUND};" + """
            color: """ + f"{THEMES_SELECT_ELEMENT};" + """
        }


        /* Link Button */
        [data-testid="stBaseLinkButton-secondary"] {
            background-color: """ + f"{THEMES_MAIN};" + """
            color: white;
            transition: all .35s ease;
            border: none;
        }

        [data-testid="stBaseLinkButton-secondary"]:hover {
            background-color: """ + f"{THEMES_SELECT_BACKGROUND};" + """
            color: """ + f"{THEMES_SELECT_ELEMENT};" + """
        }


        /* Expander */
        [data-testid="stExpander"] {
            # background-color: """ + f"{THEMES_MAIN};" + """
            # color: white;
            border: 0px solid;
            border-radius: 8px; /* Make sure the container has rounded corners */
        }

        [data-testid="stExpander"] details summary {
            color: white;
            background-color: """ + f"{THEMES_MAIN};" + """
            border: 0px solid;
            border-radius: 8px; /* Make sure the container has rounded corners */
        }

        [data-testid="stExpanderDetails"] {
            margin-top: 12px;
        }

        [data-testid="stExpander"] details:hover summary {
            color: white;
        }

        [data-testid="stPopover"] .active {
            color: white;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


def create_page_setup(page_name: str) -> None:
    create_page_config(page_name)
    create_header_bar()
    create_sidebar()

    inject_html_styling()

    # If navigating away from the search page - save the previous conversation if it exists before its lost.
    save_conversation_to_csv()

    



