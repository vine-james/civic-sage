import pandas as pd
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw
import requests
import boto3
from requests_aws4auth import AWS4Auth

import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space

import utils.constants as constants
import utils.plot_utils as plot_utils
import utils.boto_utils as boto_utils
import utils.streamlit_utils as st_utils

# NOTE: Has to be done before any other command. Just for dashboard page.
st_utils.create_page_setup(page_name="Dashboard", layout="wide")

chart_setup_functions = {
    "sessions_by_ward": plot_utils.plot_sessions_by_ward,
    "political_knowledge_by_ward": plot_utils.plot_political_knowledge_by_ward,
    "conversations_by_hour": plot_utils.plot_conversations_by_hour,
    "conversations_by_length": plot_utils.plot_conversations_by_length,
    "conversations_by_messages": plot_utils.plot_conversations_by_messages,
    "sessions_by_day": plot_utils.plot_sessions_by_day,
    "median_sentiment_by_day": plot_utils.plot_median_sentiment_by_day,
    "median_stance_by_day": plot_utils.plot_median_stance_by_day,
    "median_ideology_by_day": plot_utils.plot_median_ideology_by_day,
    "top_keywords_by_week": plot_utils.plot_top_keywords_by_week,
    "top_web_keywords_by_week": plot_utils.plot_top_web_keywords_by_week,
    "reported_responses_by_day": plot_utils.plot_reported_responses_by_day,
    "sensitive_messages_by_day": plot_utils.plot_sensitive_messages_by_day,
    "top_keywords_reports_by_week": plot_utils.plot_top_keywords_reports_by_week,
}

MPS = {
    "Paul Holmes": {"Constituency": "Hamble Valley", "Party": "Conservative"},
    "Jessica Toale": {"Constituency": "Bournemouth West", "Party": "Labour"},
    "Tom Hayes": {"Constituency": "Bournemouth East", "Party": "Labour"},
}


def create_chart(mp_name, mp_constituency, file_name, mp_data):
    chart_setup_functions[file_name](mp_data[file_name]["Data"], mp_name, mp_constituency)
    st.badge(f"Data: **{mp_data[file_name]['Date']}**", color="blue", icon=":material/monitoring:")


def preload_chart_data_into_session_state():
    # Have to pre-load into memory otherwise every button interaction 
    print("GRABBING ALL CHART DATA!")

    st.session_state.chart_data = {}

    for mp_name, mp_dict in MPS.items():
        st.session_state.chart_data[mp_name] = {}

    chart_data = boto_utils.s3_batch_get_all_files()
    for chart_dict in chart_data:

        # If chart is not a empty folder
        if chart_dict["content"] != b"":
            mp_name = chart_dict["filename"].split("/")[0]
            file_name = chart_dict["filename"].split("/")[1][:-4][6:]

            st.session_state.chart_data[mp_name][file_name] = {"Data": pd.read_csv(BytesIO(chart_dict["content"])), "Date": chart_dict["modified"].strftime("%d/%m/%y %H:%M")}
            # NOTE: For now just doing month files, so will manually remove "month" but if were adding year files would have to edit this later


def load_mp_image_into_session_state():
    mp_name = st.session_state["mp_selector"].split("(")[0][:-1]

    print(f"Loading & cropping {mp_name} portrait into session state")

    dashboard_summary_data = st_utils.get_mp_summary_from_db(mp_name)
    portrait_response = requests.get(f"{dashboard_summary_data['Picture']}?cropType=1")
    if portrait_response.status_code == 200:

        image = Image.open(BytesIO(portrait_response.content)).convert("RGBA")
        size = min(image.size)
        mask = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)
        width, height = image.size
        left = (width - size) // 2
        top = (height - size) // 2
        image_circular = image.crop((left, top, left + size, top + size))
        image_circular.putalpha(mask)

        st.session_state.portrait_data_dashboard = image_circular
        st.session_state.portrait_data_dashboard_mp = mp_name

    else:
        st.error(f"Failed to fetch the image. HTTP Status Code: {portrait_response.status_code}")


def chart_setup(mp_name, mp_constituency):
    current_period = datetime.now().strftime("%b %Y")

    mp_data = st.session_state.chart_data[mp_name]

    tab_mp, tab_civic_sage = st.tabs([f":material/id_card: MP Insights", ":material/smart_toy: Civic Sage Insights"])

    with tab_mp:
        headline_cols = st.columns([1, 1, 1])

        with headline_cols[2]:
            st.info(f"""
            **TERMINOLOGY:**
                    
            **Local Users** refer to sessions where the detected location is within **{mp_constituency}**.

            **External Users** refer to sessions where the detected location is outside of **{mp_constituency}**.
            """, icon=":material/article:")
        
        
        with headline_cols[0]:
            st.subheader("Number of Sessions (Week)")
            add_vertical_space(1)
            st.badge(f"Data: **{mp_data["sessions_by_day"]['Date']}**", color="blue", icon=":material/monitoring:")
            sub_cols = st.columns([1, 1])

            with sub_cols[0]:
                plot_utils.get_metric_sum_sessions(
                    df=mp_data["sessions_by_day"]["Data"],
                    metric_title=":material/home: **Local Users**",
                    region_type="Inside",
                    column="Sessions",
                )

            with sub_cols[1]:
                plot_utils.get_metric_sum_sessions(
                    df=mp_data["sessions_by_day"]["Data"],
                    metric_title=":material/public: **External Users**",
                    region_type="Outside",
                    column="Sessions",
                )
            

        with headline_cols[1]:

            st.subheader("Median Positive Sentiment (Week)")
            add_vertical_space(1)
            st.badge(f"Data: **{mp_data["median_sentiment_by_day"]['Date']}**", color="blue", icon=":material/monitoring:")
            sub_cols = st.columns([1, 1])

            with sub_cols[0]:
                plot_utils.get_metric_median_sentiment(
                    df=mp_data["median_sentiment_by_day"]["Data"],
                    metric_title=":material/home: **Local Users**",
                    region_type="Inside",
                    column="Positive",
                )

            with sub_cols[1]:
                plot_utils.get_metric_median_sentiment(
                    df=mp_data["median_sentiment_by_day"]["Data"],
                    metric_title=":material/public: **External Users**",
                    region_type="Outside",
                    column="Positive",
                )

        st.divider()

        st.subheader(f"Who is searching for {mp_name}? ({current_period})")
        who_cols = st.columns([1, 1])

        with who_cols[0]:
            create_chart(mp_name, mp_constituency, "political_knowledge_by_ward", mp_data)

        with who_cols[1]:
            add_vertical_space(5)
            create_chart(mp_name, mp_constituency, "sessions_by_ward", mp_data)


        st.divider()
        st.subheader(f"What themes are related to searches for {mp_name}? ({current_period})")
        what_searches_cols_1 = st.columns([1, 1])
        what_searches_cols_1 = st.columns([1, 1])


        with what_searches_cols_1[0]:
            create_chart(mp_name, mp_constituency, "top_keywords_by_week", mp_data)


        with what_searches_cols_1[1]:
            create_chart(mp_name, mp_constituency, "top_web_keywords_by_week", mp_data)

            with st.expander("Caveats", icon=":material/error:"):
                st.write("""
                - 'AI websearch responses' are Civic Sage's replies to user prompts where it could retrieve no relevant database information, thus requiring it to search the internet.
                - Therefore, AI websearch responses do not contain verified information, and responses are based on Civic Sage's interpretation of the original question (which can be wrong).
                - Analysis of AI websearch keywords should be conducted with healthy skepticism.
                """)


        st.divider()
        st.subheader(f"When are people searching for {mp_name}? ({current_period})")
        when_cols_1 = st.columns([1, 1])
        when_cols_2 = st.columns([1, 1])


        with when_cols_1[0]:
            create_chart(mp_name, mp_constituency, "conversations_by_hour", mp_data)

        with when_cols_1[1]:
            create_chart(mp_name, mp_constituency, "conversations_by_length", mp_data)

        with when_cols_2[0]:
            create_chart(mp_name, mp_constituency, "conversations_by_messages", mp_data)

        with when_cols_2[1]:
            create_chart(mp_name, mp_constituency, "sessions_by_day", mp_data)


        st.divider()
        st.subheader(f"What are people feeling when searching for {mp_name}? ({current_period})")
        feeling_cols_1 = st.columns([1, 1])
        feeling_cols_2 = st.columns([1, 1])

        with feeling_cols_1[0]:
            create_chart(mp_name, mp_constituency, "median_sentiment_by_day", mp_data)

        with feeling_cols_1[1]:
            create_chart(mp_name, mp_constituency, "median_stance_by_day", mp_data)

        with feeling_cols_2[0]:
            create_chart(mp_name, mp_constituency, "median_ideology_by_day", mp_data)
    

    with tab_civic_sage:
        cs_cols_1 = st.columns([1, 1])
        cs_cols_2 = st.columns([1, 1])

        with cs_cols_1[0]:
            create_chart(mp_name, mp_constituency, "reported_responses_by_day", mp_data)

        with cs_cols_1[1]:
            create_chart(mp_name, mp_constituency, "sensitive_messages_by_day", mp_data)
            
        with cs_cols_2[0]:
            create_chart(mp_name, mp_constituency, "top_keywords_reports_by_week", mp_data)


if "charts_preloaded" not in st.session_state:
    st.session_state.charts_preloaded = False


if not st.session_state.charts_preloaded:
    # Doing this because getting the chart data from S3 every page reload (which can happen at any time, even with a button press) would be
    # extremely computationally expensive, and must reduce this however I can. Not sure if storing all in memory is even practical
    preload_chart_data_into_session_state()

    st.session_state.charts_preloaded = True


def run():
    # Run the dashboard
    col_select_mp, _, col_fetch_data = st.columns([25, 1, 5])

    with col_select_mp:
        mp_options = [f"{mp_name} ({mp_dict['Constituency']})" for mp_name, mp_dict in MPS.items()]
        
        mp_selected = st.selectbox(":material/person: Select a MP", mp_options, on_change=load_mp_image_into_session_state, key="mp_selector")
        
        if "portrait_data_dashboard" not in st.session_state:
            load_mp_image_into_session_state()

    with col_fetch_data:
        add_vertical_space(2)

        placeholder_container = st.empty()
        with placeholder_container:
            if st.button("Fetch Latest Data", icon=":material/cloud_download:", help="This will force the system to grab, and generate analysis for, the latest data on all registered MPs. This is done automatically once every 24 hours."):
                
                with placeholder_container:
                    with st.spinner("Fetching Latest Data...", show_time=True):
                        session = boto3.Session(
                            aws_access_key_id=constants.TOKEN_AWS_ACCESS,
                            aws_secret_access_key=constants.TOKEN_AWS_SECRET,
                            region_name=constants.AWS_REGION,
                        )

                        credentials = session.get_credentials().get_frozen_credentials()
                        awsauth = AWS4Auth(
                            credentials.access_key,
                            credentials.secret_key,
                            session.region_name,
                            "lambda",
                            session_token=credentials.token
                        )
                        
                        response = requests.post(constants.AWS_URL_ANALYSE_FUNCTION, auth=awsauth, json={"hello": "world"})
                        st.write(response.json())

                        preload_chart_data_into_session_state()
                        st.session_state.charts_preloaded = True

                        st.rerun()

    st.divider()

    for option in mp_options:
        if mp_selected == option:
            with st.container():
                mp_name = mp_selected.split("(")[0][:-1]
                mp_dict = MPS[mp_name]

                mp_constituency = mp_dict["Constituency"]
                mp_party = mp_dict["Party"]
                party_colour = st_utils.PARTY_THEMES[mp_party]

                profile_cols = st.columns([1, 20])
                
                with profile_cols[0]:
                    # NOTE: Due to way streamlit handles re-running selectable elements, need to account for changing page by sidebar, which
                    # -retains session state (keeping old picture), but resetting other elements e.g. selectboxes
                    if st.session_state.portrait_data_dashboard_mp != mp_name:
                        print("RELOADING PORTRAIT, IMAGE DOES NOT MATCH CURRENT MP")
                        load_mp_image_into_session_state()
                        
                    st.image(st.session_state.portrait_data_dashboard)
                
                with profile_cols[1]:
                    st.markdown(f"""
                    <p style='line-height: 1; font-size: 34px; font-weight: bold;'>{mp_name}</p>
                    <p style='line-height: 0; font-size: 26px;'><span style='color: {party_colour};'>{mp_party}</span> MP for <b>{mp_constituency}</b></p>
                    """, unsafe_allow_html=True)

                add_vertical_space(1)
                
                chart_setup(mp_name, mp_constituency)

    st.markdown(
        """
        <style>
        /* Reduce margin above the badge */
        .is-badge {
            margin-top: -4rem !important;
            margin-bottom: 0rem !important;
            display: inline-block !important;
        }

        .stExpander {
            margin-top: -2.25rem !important;
            margin-bottom: 0rem !important;
            display: inline-block !important;
        }

        .stMetric {
            margin-top: -2.5rem !important;
            margin-bottom: 0rem !important;
            display: inline-block !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


@st.dialog("Login to the User Dashboard")
def login():
    st.info("**TESTERS:** The password is   `test`", icon=":material/construction:")
    password_input = st.text_input("Enter Password", type="password")
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