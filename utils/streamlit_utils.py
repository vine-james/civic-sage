import streamlit as st
import requests

import utils.constants as constants

THEMES_MAIN = "#3087ff"

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


def create_sidebar() -> None:
     with st.sidebar:
        # Logo, Title, Version
        # st.image(constants.PATH_IMAGES / "civic-sage-logo.png")

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
        st.info("**REVIEWERS:** Are you testing this artefact as part of a requested survey? Access the [JISC Survey form here](google.com). This is the only acceptable way to provide feedback.")

        


def create_page_config(page_name: str) -> None:
    st.set_page_config(
        page_title=f"Civic Sage | {page_name}",
        page_icon="🗳️",
        layout="centered",
        initial_sidebar_state="expanded",
    )


def create_elements_theming() -> None:
    return None


def create_page_setup(page_name: str) -> None:
    create_page_config(page_name)
    create_header_bar()
    create_sidebar()

    # TODO
    create_elements_theming()



