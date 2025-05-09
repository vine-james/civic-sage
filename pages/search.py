from datetime import datetime
from langchain_core.messages import AIMessage
import time

import streamlit as st
from streamlit_extras.bottom_container import bottom 
from streamlit_extras.add_vertical_space import add_vertical_space

import utils.streamlit_utils as st_utils
import utils.location_utils as location_utils

st_utils.create_page_setup(page_name="Search")

# Save setup options as constants
PAGE_SETUP_FIND_MP = "Find an MP"
PAGE_SETUP_SEARCH_LLM = "Search LLM"


# Minimal required page setup behaviour for the 'Find an MP' segment
def page_setup_find_mp():
    st.title(":material/search: Search for an MP")
    st.write("To select an MP, use one of the buttons below.")

    col_location, col_search, _, _ = st.columns([1, 1, 1, 1])
    st.divider()

    with col_location:
        if st.button("Find my MP by **my location**", icon=":material/pin_drop:"):
            st.session_state.search_option = "Location"

    with col_search:
        if st.button("Search for an MP **manually**", icon=":material/person_search:"):
            st.session_state.search_option = "Manual"


# Minimal required page setup behaviour for the 'Search LLM (based on your found MP)' segment
def page_setup_search_llm():

    CURRENT_MP = st.session_state.current_mp

    # ChatHistory and User through st.session_state through the usage agreement
    if "location" not in st.session_state:
        print("Running Location Setup")
        latitude, longitude = location_utils.get_location_by_streamlit()
        st.session_state.location = (latitude, longitude)

    if "usage_agreement" not in st.session_state:
        st_utils.usage_agreement_and_init_setup(CURRENT_MP)


    # Has to be hidden within a one-time action chain as otherwise it will call the AWS boto API constantly
    if "mp_summary_data" not in st.session_state:
        st.session_state.mp_summary_data = st_utils.get_mp_summary_from_db(CURRENT_MP)


    st_utils.setup_mp_summary_details(CURRENT_MP, st.session_state.mp_summary_data)


    # Run chat history if a chat history exists (to prevent first-run error)
    if "chat_history" in st.session_state:
        # Send intro message, which is never logged as part of the chat history due to its independent send nature (outside of rag_llm_utils)
        if "intro_sent" not in st.session_state:
            # If no chat history, send the "start message" for the conversation.
            st_utils.send_chat_message({"role": "ai", "message": AIMessage(f"Hi there! Feel free to ask me to explain any political information about {CURRENT_MP}!"), "time": datetime.now(), "message_index": None}, speak=True)
            st.session_state.intro_sent = True
        else:
            st_utils.send_chat_message({"role": "ai", "message": AIMessage(f"Hi there! Feel free to ask me to explain any political information about {CURRENT_MP}!"), "time": datetime.now(), "message_index": None}, speak=False)


        st_utils.process_chat_history()
    
    # Run-time
    chat_placeholder = st.empty()

    # Footer
    with bottom():
        # Disclaimer
        st.markdown(f"""
            <p style='line-height: 0; font-size: 14px; text-align: center; color: #9c9d9f;'>Civic Sage can make mistakes. Always verify important information.</p>
        """, unsafe_allow_html=True)

        # Footer-sub columns for positioning
        col_samples, col_chat = st.columns([1, 7])

        # Sample questions to ask from a button popover
        with col_samples:
            # Make sure you can port this out. We dont want a giant paragraph
            with st.popover("", icon=":material/help:", help="Select from a list of sample questions"):
                st.markdown(f"<div style='text-align: center'>Popular search terms for users interested in <b>{CURRENT_MP}</b> are:<br><i>{st.session_state.mp_keywords}</i></div>", unsafe_allow_html=True)
                add_vertical_space(1)

                suggested_prompts = [f"What is {CURRENT_MP}'s recent voting record?", f"What declared payments has {CURRENT_MP} received?", f"When was {CURRENT_MP} elected?"]
                button_cols = st.columns([1 for _ in suggested_prompts])

                for i, button_col in enumerate(button_cols):
                    with button_col:
                        if st.button(f":material/search: {suggested_prompts[i]}"):
                            with chat_placeholder.container():
                                time.sleep(.1)
                                st_utils.process_prompt_and_response(suggested_prompts[i], st.session_state.user, CURRENT_MP, st.session_state.mp_summary_data["Constituency"])
            
        # Dialog system - Enter a question through streamlit chatbox
        with col_chat:
            prompt = st.chat_input(f"Enter a question regarding {CURRENT_MP}")


    # If value inside chat input found, begin the question-answer behaviour
    if prompt:
        with chat_placeholder.container():
            time.sleep(.1)
            st_utils.process_prompt_and_response(prompt, st.session_state.user, CURRENT_MP, st.session_state.mp_summary_data["Constituency"])


# FIRST SET-UP
if "current_page_function" not in st.session_state:
    st.session_state.current_page_function = PAGE_SETUP_FIND_MP

    # For handling who is the current MP being searched
    st.session_state.current_mp = None


# Determine which section to show based on set session state of current_page_function
if st.session_state.current_page_function == PAGE_SETUP_FIND_MP:
    page_setup_find_mp()

    if "search_option" not in st.session_state:
        st.session_state.search_option = None

    if st.session_state.search_option == "Location":
        st_utils.query_location()

    if st.session_state.search_option == "Manual":
        st_utils.query_manually()

elif st.session_state.current_page_function == PAGE_SETUP_SEARCH_LLM:
    page_setup_search_llm()
