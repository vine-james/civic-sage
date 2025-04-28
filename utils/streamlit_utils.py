
import pandas as pd
import requests
import re
from PIL import Image
from io import BytesIO, StringIO
from datetime import datetime, timedelta
import uuid
import time
from langchain_core.messages import HumanMessage, AIMessage

import streamlit as st
from streamlit_searchbox import st_searchbox
from streamlit_theme import st_theme

import utils.constants as constants

import utils.rag_llm_utils as rag_llm_utils
import utils.boto_utils as boto_utils
import utils.analysis_utils as analysis_utils
import utils.location_utils as location_utils


THEMES_MAIN = "#3087ff"
THEMES_SELECT_BACKGROUND = "#e3e7ee"
THEMES_SELECT_ELEMENT = "#1d2345"
SPEECH_DELAY = 0.1

# Only covering main parties currently, as the ones in our analysis are Conservative, Labour.
PARTY_THEMES = {
    "Conservative": "#0087dc",
    "Labour": "#e4003b",
    "Liberal Democrats": "#FDBB30",
}

# Instantiate table here - may need to amend this later
message_reports_table = boto_utils.dynamodb_init("message-reports")



def get_version():
    try:
        response = requests.get(
            url="https://api.github.com/repos/vine-james/civic-sage/releases/latest", 
            headers={"Authorization": f"Bearer {constants.TOKEN_GITHUB}"}, 
            timeout=10
        )

        if response.status_code == 200:
            return response.json().get("tag_name", "No version found")[1:]
        
        else:
            print(f"Error: Unable to fetch version (HTTP {response.status_code})")
            return "Unavailable"
        
    except Exception:
        print("Error: Unable to connect to GitHub")
        return "Unavailable"


def create_header_bar():
   st.markdown("""
        <style>
            [data-testid="stDecoration"] {
                background:""" + f"{THEMES_MAIN};" + """
                height: 12%;
            }
        </style>
        """, unsafe_allow_html=True) 


def create_sidebar():
    with st.sidebar:
        # Logo, Title, Version
        st.image(constants.PATH_IMAGES / "civic-sage-logo.png", width=160)
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

        st.divider()

        # Dissertation review notice
        with st.expander("**Survey Feedback**", icon=":material/feedback:"):
            st.info("**REVIEWERS:** Are you testing this artefact as part of a requested survey? Access the [JISC Survey form here](https://app.onlinesurveys.jisc.ac.uk/s/bournemouth/dissertation-response-survey). This is the only acceptable way to provide feedback.")
            st.image(constants.PATH_IMAGES / "survey-qr-code.png")


def create_page_config(page_name, layout):
    st.set_page_config(
        page_title=f"Civic Sage | {page_name}",
        page_icon="🗳️",
        layout=layout,
        initial_sidebar_state="expanded",
    )


def inject_html_styling():
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


def create_page_setup(page_name, layout="centered"):
    create_page_config(page_name, layout)
    create_header_bar()
    create_sidebar()

    inject_html_styling()


def get_mps_keywords(mp_name):
    print("GETTING MP KEYWORDS")

    # Get the top keywords (as analysed by top_keywords_by_week.csv) from S3 bucket for search page recommendations
    keyword_data = boto_utils.s3_get_file(f"{mp_name}/month_top_keywords_by_week.csv")

    # If keyword data returns nothing (no analysis file, return default output)
    keywords_output = "No historical search terms found. You're the first!"

    if keyword_data:
        df_col = pd.DataFrame(StringIO(keyword_data))
        df_keywords = df_col[0].str.strip().str.split(',', expand=True)
        df_keywords.columns = df_keywords.iloc[0]
        df_keywords = df_keywords[1:]

        df_keywords_list = df_keywords["Top Keyword"].to_list()

        keywords_stripped = [message for message in df_keywords_list if message != "No data available"]

        # If array is not empty (so if there are still keywords)
        if keywords_stripped:
            keywords_latest_first = keywords_stripped[::-1]
            keywords_first_four = keywords_latest_first[:4]
            keywords_output = ", ".join(keywords_first_four)
            
    return keywords_output


@st.dialog("Civic Sage Usage Agreement")
def usage_agreement_and_init_setup(mp_name):
    st.write("**Please rate**: How much, if anything do you feel you know about:")

    select_options = ["Nothing at all", "Not very much", "A fair amount", "A great deal"]

    user_knowledge_politics = st.select_slider("UK Politics", select_options)
    user_knowledge_parliament = st.select_slider("UK Parliament", select_options)
    user_knowledge_government = st.select_slider("UK Government", select_options, help="Confused about the difference between 'Parliament' and 'Government'? If so, please select the default 'Nothing at all'.")

    st.divider()

    st.write("""
    **Conditions of usage**:
             
    > While using Civic Sage, both **your :material/chat: prompts/messages** & :material/pin_drop: **location data** will be stored, personal information anonymised, then aggregated for group-wide analysis of user behaviour and interest. Your *individual* conversation will **NOT** be viewed. However, please do not include any private or sensitive information as part of your conversation.
    """)

    confirm = st.checkbox("**I agree to the conditions set out above while using Civic Sage.**")

    # This has to be done before submitting, as code outside of the function after the if statement relies on it
    if "mp_keywords" not in st.session_state:
        st.session_state.mp_keywords = get_mps_keywords(mp_name)

    submit = st.button("Continue", disabled=not confirm)
    if submit:
        # Set up user and chat history.
        st.session_state.usage_agreement = True

        chat_history = rag_llm_utils.init(ch=rag_llm_utils.ChatHistory(size=20))

        st.session_state.user = rag_llm_utils.User(competencies={
            "UK Politics": user_knowledge_politics,
            "UK Parliament": user_knowledge_parliament,
            "UK Government": user_knowledge_government,
        })

        st.session_state.chat_history = chat_history

        st.session_state.session_start = datetime.now()

        # Finally, re-run the app to get rid of the screen
        st.rerun()


@st.dialog("Report a mistake in a Civic Sage response")
def report_message(message, message_index) -> None:

    st.write(":material/speaker_notes_off: Reported Response:")
    block_col, reported_response = st.columns([1, 20])
    with block_col:
        st.markdown("""
        <div style="background-color: #808080; width: 40%; height: 1000%;">
        </div>
        """, unsafe_allow_html=True)
    with reported_response:
        st.caption(message)

    st.divider()

    reported_tags = st.pills(":material/label: How would you tag the response error? [Multi-select]", ["Inaccurate information", "Inaccurate sources", "Political bias", "Explanation not understandable", "Other"], selection_mode="multi")

    comments = st.text_area(
        ":material/rate_review: Enter any additional comments below:",
        ""
    )

    if st.button("Submit", disabled=(reported_tags is None)):
        st.session_state.report_submitted = True

        previous_messages = st.session_state.chat_history.get_reported_message_context(message_index)
        previous_messages_anonymised = [analysis_utils.anonymize_text(message, st.session_state.current_mp) for message in previous_messages]

        boto_utils.dynamodb_upload_record(
            message_reports_table,
            {
                # Partition key
                "mp_name": st.session_state.current_mp,

                # Sort key (PK = partition key + sort key)
                "message_reported_datetime": str(datetime.now()),

                "Response": message,
                "Reported Tags": reported_tags,
                "Reportee Comments": comments,

                # Get last 5 messages
                "Previous Messages": previous_messages_anonymised,

            },
        )

        st.success("**Report submitted successfully**\n\nThank you for your feedback!\nThis information will be assessed by a human reviewer.", icon=":material/task_alt:")

        dismiss_bar = st.progress(0, text=None)
        time_to_read = 3

        for percent_complete in range(100):
            time.sleep(time_to_read / 100)
            dismiss_bar.progress(percent_complete + 1, text=None)
        time.sleep(1)
        st.rerun()


def convert_datetime_str(datetime_str):
    if datetime_str is None:
        return "Current"

    return datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S").strftime("%d/%m/%Y")


def get_mp_continuous_serving_period(mp_elections):
    # Find the most recent "Won election"
    current_constituency = None
    current_start_date = None
    for election in mp_elections:
        if election["Result"] == "Won election":
            current_constituency = election["Constituency"]
            current_start_date = datetime.strptime(election["Date"], "%Y-%m-%dT%H:%M:%S")
            break

    # Check for breaks in continuity (e.g., a "Lost election" in the same constituency afterward)
    for election in mp_elections:
        election_date = datetime.strptime(election["Date"], "%Y-%m-%dT%H:%M:%S")
        if election_date > current_start_date and election["Constituency"] == current_constituency:
            if election["Result"] == "Lost election":
                return "The MP is not currently serving in any constituency."
            

    return current_start_date.strftime("%d/%m/%Y")


def get_mp_summary_from_db(mp_name):
    # Function to call database and get details for that specific MP
    boto_table = boto_utils.dynamodb_init("summaries")
    mp_summary_data = boto_utils.dynamodb_fetch_record(boto_table, "mp_name", mp_name)

    return mp_summary_data

    
def setup_mp_summary_details(mp_name, mp_summary_data):
    # NOTE: Temporary notice for testing
    st.info("**TESTERS:** To save your conversation for analysis, you **must** use the **:material/arrow_back: button** to exit the page due to current platform limitations. Occasionally, this may take some time to process.", icon=":material/construction:")

    # Structure
    col_portrait, col_content = st.columns([1, 3], gap="small")

    # Portrait
    with col_portrait:
        if "portrait_data" not in st.session_state:
            # print("GETTING PORTRAIT")
            portrait_response = requests.get(f"{mp_summary_data['Picture']}?cropType=3")
            if portrait_response.status_code == 200:
                st.session_state.portrait_data = BytesIO(portrait_response.content)

            else:
                st.error(f"Failed to fetch the image. HTTP Status Code: {portrait_response.status_code}")

        # Convert the response content into an image
        portrait = Image.open(st.session_state.portrait_data)

        new_height = portrait.height + int(portrait.height * 0.1)
        new_image = Image.new("RGB", (portrait.width, new_height), PARTY_THEMES[mp_summary_data["Party"]])
        new_image.paste(portrait, (0, 0))

        st.image(new_image, width=150, caption=f"{mp_name} © House of Commons")
                
    with col_content:
        col_summary, col_button = st.columns([6, 1])
        with col_summary:
            st.markdown(f"""
            <p style='line-height: 1; font-size: 28px; font-weight: bold;'>{mp_name}</p>
            <p style='line-height: 0; font-size: 20px;'>Member of Parliament for <b>{mp_summary_data['Constituency']}</b></p>
            """, unsafe_allow_html=True)

            st.markdown(
                f"<p style='line-height: 0.8; font-size: 16px;'>{get_mp_continuous_serving_period(mp_summary_data['Elections'])} - Current</p>",
                help="This date range reflects the period of only their **current** constituency. They may have served as an MP prior in a different constituency. If unsure, view their political career history.",
                unsafe_allow_html=True
            )

            st.markdown(f"<p style='font-size: 20px; color: {PARTY_THEMES[mp_summary_data['Party']]};'>{mp_summary_data['Party']}</p>", unsafe_allow_html=True)
        
            
        # Back button to return to finding an MP
        with col_button:
             if st.button("", icon=":material/arrow_back:"):
                # Check that any chat history exists
                if len(st.session_state.chat_history.all_messages) > 0:
                    analysis_utils.analyse_chat(st.session_state)
                del st.session_state.current_mp
                del st.session_state.mp_summary_data
                del st.session_state.portrait_data
                del st.session_state.mp_keywords
                del st.session_state.usage_agreement
                st.session_state.current_page_function = "Find an MP"
                st.rerun()


        with st.expander(f"Find {mp_name} online", icon=":material/share:"):
            contact_types = ["Website", "Facebook", "X (formerly Twitter)"]
    
            contact_cols = st.columns([1, 1, 1, 1])

            with contact_cols[0]:
                st.link_button(f"Email :material/arrow_outward:", f"mailto:{mp_summary_data['Email']}")

            current_col = 0

            for contact_type in contact_types:
                if mp_summary_data.get(contact_type):
                    current_col += 1
                    with contact_cols[current_col]:
                        st.link_button(f"{contact_type} :material/arrow_outward:", mp_summary_data[contact_type])

        with st.expander(f"See {mp_name}'s political career history", icon=":material/id_card:"):
            tab_elections, tab_gov, tab_opposition, tab_committees = st.tabs([":material/how_to_vote: Elections", ":material/account_balance: Gov Posts", ":material/mystery: Opposition Posts", ":material/adaptive_audio_mic: Committees"])
            
            with tab_elections:                
                if mp_summary_data["Elections"]:
                    for election_dict in mp_summary_data["Elections"]:
                        st.write(f"- {convert_datetime_str(election_dict['Date'])}: **{election_dict['Result']}** in the constituency of **{election_dict['Constituency']}**")
                else:
                    st.write(f"{mp_name} has no previous elections recorded where they ran to become a Member of Parliament.")

            with tab_gov:
                if mp_summary_data["Government Posts Held"]:
                    for post_dict in mp_summary_data["Government Posts Held"]:
                        st.write(f"""- **{post_dict['Post']}** :grey-badge[:material/work: {post_dict['Department']}]
                                \n  :material/calendar_month: {convert_datetime_str(post_dict['Start'])} - {convert_datetime_str(post_dict['End'])}""")

                else:
                    st.write(f"{mp_name} has no current or previous Government posts.")

            with tab_opposition:
                if mp_summary_data["Government Posts Held"]:
                    for post_dict in mp_summary_data["Opposition Posts Held"]:
                        st.write(f"""- **{post_dict['Post']}** :grey-badge[:material/work: {post_dict['Department']}]
                                \n  :material/calendar_month: {convert_datetime_str(post_dict['Start'])} - {convert_datetime_str(post_dict['End'])}""")
                else:
                    st.write(f"{mp_name} has no current or previous Opposition posts.")


            with tab_committees:
                if mp_summary_data["Committee Memberships Held"]:
                    for post_dict in mp_summary_data["Committee Memberships Held"]:
                        st.write(f"""- **{post_dict['Post']}**
                                \n  :material/calendar_month: {convert_datetime_str(post_dict['Start'])} - {convert_datetime_str(post_dict['End'])}""")

                else:
                    st.write(f"{mp_name} has no current or previous Parliamentary committee memberships.")         


def process_source_text(input_text):
    urls = re.findall('\\[SOURCE URL: [^\\]]+\\]', input_text)

    url_list = []
    
    for i, text_extract in enumerate(urls, start=1):
        url = text_extract[13:][:-1]
        url_list.append((i, url))

        input_text = input_text.replace(text_extract, f":violet-badge[:material/document_search: [{i}]({url})]", 1)

    source_text = "\n".join([f"{source_tuple[0]}. {source_tuple[1]}" for source_tuple in url_list])
    
    return input_text, source_text


def format_datetime(input_datetime):
    now = datetime.now()
    # Check if the input is less than a day old
    if now - input_datetime < timedelta(days=1):
        return input_datetime.strftime("%H:%M")
    else:
        return input_datetime.strftime("%d/%m/%y %H:%M")


def speak_ai_response(message):
    for word in message.split(" "):
        yield word + " "
        time.sleep(SPEECH_DELAY)


def send_chat_message(chat_message_dict, speak=False):
    # Set up chat entry
    with st.chat_message(chat_message_dict["role"]):

        # IF = AI - Write response with special embeds/set-up
        if chat_message_dict["role"] == "ai":

            # First identify components of the response.
            llm_message = chat_message_dict["message"].content
            llm_sources = None
            llm_web_search = None
            llm_sensitive_reply = None

            if "[SOURCE URL:" in llm_message:
                llm_message, llm_sources = process_source_text(llm_message)

            if "WEB SEARCH:" in llm_message:
                llm_message = llm_message.split("WEB SEARCH:")[1]
                llm_web_search = True

            if "SENSITIVE REPLY:" in llm_message:
                llm_message = llm_message.split("SENSITIVE REPLY:")[1]
                llm_sensitive_reply = True

            # Header title
            st.markdown(f"""
                <div style="display: flex; margin-top: 10px;">
                    <p style='font-size: 18px; line-height: 0px; color: {THEMES_MAIN};'><b>Civic Sage</b></p>
                    <p style='font-size: 14px; line-height: 0px;'>&nbsp;&nbsp;&nbsp;• &nbsp;&nbsp; {format_datetime(chat_message_dict["time"])}</p>
                </div>
            """, unsafe_allow_html=True)

            if llm_web_search:
                st.warning("This response uses content from a websearch. Information should be manually verified.", icon=":material/language:")

            if llm_sensitive_reply:
                st.error("If you are in immediate danger or facing an emergency, please call 999 or [contact the relevant emergency services immediately](https://join.humber.nhs.uk/international-welcome-hub/emergency-contacts/).\n\nCivic Sage cannot provide assistance in urgent or life-threatening situations.", icon=":material/emergency_home:")

            # Messages are re-loaded in every dialog turn, so throw all of the history in. If it's the CURRENT LLM response, 'speak/write' it instead for effect.
            if speak:
                st.write_stream(speak_ai_response(llm_message))
            else:
                st.write(llm_message)

            # Sources & Report Response footers
            col_1, col_2 = st.columns([5, 1])

            # Sources
            with col_1:
                if llm_sources:
                    with st.expander("Sources", icon=":material/document_search:"):
                        st.markdown(llm_sources, unsafe_allow_html=True)

            # Report Response - check that its a response that can be reported (aka not the first message)
            if chat_message_dict["message_index"]:
                with col_2:
                    st.button("", icon=":material/thumb_down:", help="Spotted a mistake in Civic Sage's response? Click me to report the message.", on_click=report_message, args=(llm_message, chat_message_dict["message_index"]), key=str(uuid.uuid4()))


        # IF = USER - Write response normally
        else:
            st.markdown(f"""
                <div style="display: flex; margin-top: 10px;">
                    <p style='font-size: 14px; line-height: 0px;'>{format_datetime(chat_message_dict["time"])}</p>
                </div>
            """, unsafe_allow_html=True)
            st.write(chat_message_dict["message"].content)


# Process a question and answer
def process_prompt_and_response(prompt, llm_user, current_mp, current_mp_constituency):

    # 1. Visually display prompt on conversation log
    send_chat_message({"role": "user", "message": HumanMessage(content=prompt), "time": datetime.now()})

    # 2. Process prompt through LLM pipeline. It also:
        # Stores/maintains chat history obj.
    st.write("")
    with st.spinner(":material/network_intelligence: Civic Sage is thinking...", show_time=True):
        llm_response, llm_response_index = rag_llm_utils.ask_prompt(prompt, llm_user, current_mp, current_mp_constituency)

    # 3. Return LLM response
    send_chat_message({"role": "ai", "message": AIMessage(llm_response), "time": datetime.now(), "message_index": llm_response_index}, speak=True)


def process_chat_history():
    full_chat_history = st.session_state.chat_history.all_messages

    for chat_message_dict in full_chat_history:
        if isinstance(chat_message_dict["message"], HumanMessage):
            send_chat_message({"role": "user", "message": chat_message_dict["message"], "time": chat_message_dict["time"], "message_index": chat_message_dict["message_index"]})

        elif isinstance(chat_message_dict["message"], AIMessage):
            send_chat_message({"role": "ai", "message": chat_message_dict["message"], "time": chat_message_dict["time"],  "message_index": chat_message_dict["message_index"]})

 
# SEARCH SECTION FUNCTIONS 
full_ids = ["Paul Holmes (Hamble Valley)", "Jessica Toale (Bournemouth West)", "Tom Hayes (Bournemouth East)"]
mps = [id.split("(")[0][:-1] for id in full_ids]
constituencies = [id.split("(")[1][:-1] for id in full_ids]


def go_to_mp_query(mp_name):
    st.session_state.current_mp = mp_name
    st.session_state.current_page_function = "Search LLM"
    st.rerun()


def search(search_term):
    return full_ids


def check_constituency(searched_constituency, mp_name):
    if searched_constituency not in constituencies:
        st.warning("Unfortunately your constituency is not covered within the current Civic Sage database as part of this testing phase.\n\nWe recommend selecting an available Member of Parliament through the 'Search for an MP manually' -> 'Search by Name or Constituency' workflow. We apologise for the inconvenience.", icon=":material/error:")
        
    else:
        if st.button(f"View {mp_name}", icon=":material/search:"):
            go_to_mp_query(mp_name)
        

def query_location(session_state):
    admin_ward, postcode, constituency, mp_name = location_utils.get_mp_by_constituency(session_state)

    st.write(f"Based off your approximate location of **{admin_ward}, {postcode}** we think your constituency is **{constituency}**, which is represented by **{mp_name}**.")
    check_constituency(constituency, mp_name)


def query_manually():
    tab_search_postcode, tab_search_mp = st.tabs(["Search by Postcode", "Search by Name or Constituency"])

    with tab_search_postcode:
        postcode = st.text_input("Enter a Postcode")

        # NOTE: This set of code has to be done this way, instead of using check_constituency.
        # There seems to be behaviour where functions within 2+ levels of if-statement Streamlit buttons will not execute. This is my work-around.
        if st.button("Search Postcode"):

            pattern = r"^([A-Za-z][A-Ha-hJ-Yj-y]?[0-9][A-Za-z0-9]? ?[0-9][A-Za-z]{2}|[Gg][Ii][Rr] ?0[Aa]{2})$"
            is_postcode = re.fullmatch(pattern, postcode.strip().upper()) is not None
            # Credit to https://stackoverflow.com/questions/164979/regex-for-matching-uk-postcodes
            if is_postcode:
                constituency, mp = location_utils.get_mp_by_postcode(postcode)

                st.write(f"The MP representing **{postcode.upper()} ({constituency})** is **{mp}**.")

                if constituency not in constituencies:
                    st.warning("Unfortunately your constituency is not covered within the current Civic Sage database as part of this testing phase.\n\nWe recommend selecting an available Member of Parliament through the 'Search for an MP manually' -> 'Search by Name or Constituency' workflow. We apologise for the inconvenience.", icon=":material/error:")
                else:
                    st.button(f"View {mp}", icon=":material/search:", on_click=go_to_mp_query, args=(mp, ))

            else:
                st.warning(f"**{postcode}** does not seem to match the [expected format for UK postcodes](https://ideal-postcodes.co.uk/guides/uk-postcode-format). Please check your input and try again.\n\nPlease contact the Civic Sage developers if you believe this is an error.")


    with tab_search_mp:
        mp_name_constituency = st_searchbox(search, placeholder="Search for an MP",)

        if mp_name_constituency:
            check_constituency(mp_name_constituency.split("(")[1][:-1], mp_name_constituency.split("(")[0][:-1])