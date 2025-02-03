import streamlit as st
import utils.streamlit_utils as st_utils
import utils.gpt_utils as gpt_utils
import time
import pandas as pd
from datetime import datetime
from streamlit_extras.bottom_container import bottom 

import utils.constants as constants

st_utils.create_page_setup(page_name="Testing")

st.title("Search for an MP")

from collections import namedtuple
MP_Data = namedtuple("MP_Data", ["Portrait", "Party", "Constituency", "Tenure", "Contact", "History"])

# Store the currently selected MP dropdown box value, so that each run, if old is different to new, reset the chat history (cant figure out another way to do this)
current_selected_mp = None
if "current_selected_mp" not in st.session_state:
    st.session_state.current_selected_mp = None

# chat_messages = [
#     {"role": "ai", "message": {"content": f"Hi there! Feel free to ask me to explain any political information about {mp_name}!"}},
#     {"role": "user", "message": {"content": "What did they vote for on the assisted dying bill?"}},
#     {"role": "ai", "message": {
#         "content": "Sir Keir Starmer voted 'Aye' (yes) on the Terminally Ill Adults (End of Life) Bill: Second Reading on 29 November 2024. It subsequently passed with 330 (Ayes) to 275 (Noes) [[1]](https://google.com)",
#         "sources": "<a href='https://google.com' style='font-size: 18px'><b>[1]</b></a>: Test bla bla bla",
#         }
#     },
# ]




def get_mp_data(mp_name: str) -> namedtuple:
    mps = {
        None: None,
        "Keir Starmer": MP_Data(
            Portrait=constants.PATH_IMAGES / "Portrait_Keir.jpg",
            Party="Labour",
            Constituency="Holborn and St Pancras",
            Tenure="7 May 2015 - Present",
            Contact={"X (@keir_starmer)": "https://x.com/keir_starmer", "Parliamentary Office": "mailto:keir.starmer.mp@parliament.uk", "Constituency Office": "mailto:keir.starmer.constituency@parlaiment.uk"},
            History="Jeff",

        ),
        "Paul Holmes": MP_Data(
            Portrait=constants.PATH_IMAGES / "Portrait_Holmes.jpeg",
            Party="Conservative",
            Constituency="Hamble Valley",
            Tenure="7 December 2019 - Present",
            Contact={"X (@pauljholmes)": "https://x.com/pauljholmes", "Parliamentary Office": "mailto:paul.holmes.mp@parliament.uk", "Constituency Office": "https://google.com"},
            History="Jeff",
        ),
    }

    return mps[mp_name]


parties_main_theme = {
    "Conservative": "#0087dc",
    "Labour": "#e4003b",
    "Liberal Democrats": "#FDBB30",
    "Reform UK": 4,
}



# pass search function and other options as needed
def speak_ai_response(message):
    for word in message.split():
        yield word + " "
        time.sleep(0.1)


def format_ai_response(message):
    # return f"""
    #     <div style="display: flex; margin-top: 10px;">
    #         <p style='font-size: 18px; line-height: 0px; color: {st_utils.THEMES_MAIN};'><b>Civic Sage</b></p>
    #         {"<p style='font-size: 14px; line-height: 0px;'>&nbsp;&nbsp;&nbsp; • &nbsp;&nbsp; Data as of Jan, 2017</p>" if "sources" in message else ""}
    #     </div>

    #     <p style='font-size: 16px; line-height: 18px;'>{message["content"]}</p>
    # """

    return f"""
        <div style="display: flex; margin-top: 10px;">
            <p style='font-size: 18px; line-height: 0px; color: {st_utils.THEMES_MAIN};'><b>Civic Sage</b></p>
            {"<p style='font-size: 14px; line-height: 0px;'>&nbsp;&nbsp;&nbsp; • &nbsp;&nbsp; Data as of Jan, 2017</p>" if "sources" in message else ""}
        </div>
    """



def send_chat_message(message, speak=False):
    with st.chat_message(message["role"]):
        # AI text
        if message["role"] == "ai":
            st.markdown(format_ai_response(message["message"]), unsafe_allow_html=True)

            # As the messages are re-loaded in for every message, specifically "fake" writing the last message.
            if speak:
                st.write(speak_ai_response(message["message"]["content"]))
            else:
                st.write(message["message"]["content"])

            if "sources" in message["message"]:
                with st.expander("🔍 Sources"):
                    st.markdown(message["message"]["sources"], unsafe_allow_html=True)

        else:
            st.write(message["message"]["content"])

def process_chat_history(messages):
    # for i, message in enumerate(messages):
    for message in messages:
        send_chat_message(message)
        





from streamlit_searchbox import st_searchbox
def search(searchterm: str):
    return ["Keir Starmer", "Paul Holmes"]

st.markdown("<p style='line-height: 0; font-size: 15px;'>Search for a Member of Parliament (MP) or Constituency</p>",  unsafe_allow_html=True)
mp_name = st_searchbox(
    search,
    placeholder="...",
    key="my_key",
)

if mp_name != None:
    mp_data = get_mp_data(mp_name)

    from PIL import Image
    col1, col2 = st.columns([1, 3], gap="small")


    image = Image.open(mp_data.Portrait)

    with col1:
        border_size = 100
        new_height = image.height + border_size
        new_image = Image.new('RGB', (image.width, new_height), parties_main_theme[mp_data.Party])
        new_image.paste(image, (0, 0))  # Paste the original image

        st.image(new_image, width=150, caption=f"{mp_name} © House of Commons")

    with col2:
        st.markdown(f"""
                    <p style='line-height: 1; font-size: 28px; font-weight: bold;'>{mp_name}</p>
                    <p style='line-height: 0; font-size: 20px;'>Member of Parliament for <b>{mp_data.Constituency}</b></p>
                    <p style='line-height: 0.8; font-size: 16px;'>{mp_data.Tenure}</p>

                    <p style='font-size: 20px; color: {parties_main_theme[mp_data.Party]};'>{mp_data.Party}</p>
                    """, unsafe_allow_html=True)
        
        with st.expander(f"Find {mp_name} online"):
            cols = st.columns([1 for _ in mp_data.Contact], gap="small")
            
            for col, contact_dict in zip(cols, mp_data.Contact.items()):
                with col:
                    st.link_button(f"{contact_dict[0]} 🡭", contact_dict[1])

        with st.expander(f"See {mp_name}'s political career history"):
            st.write("-")
            # with st.expander("Previous Elections"):
            #     st.write("1")

            # with st.expander("Government/Opposition Posts"):
            #     st.write("1")

            # with st.expander("Committee Memberships"):
            #     st.write("1")

    st.divider()


     # Set up chat history
    # if "messages" not in st.session_state:
    print(st.session_state.current_selected_mp, mp_name)
    if st.session_state.current_selected_mp != mp_name:
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

        st.session_state.current_selected_mp = mp_name
        st.session_state.messages = []

        # Set up intro message
        intro_message = {"role": "ai", "date": datetime.now().strftime("%d/%m/%Y"), "time": datetime.now().strftime("%H:%M:%S"), "message": {"content": f"Hi there! Feel free to ask me to explain any political information about {mp_name}!"}}
        send_chat_message(intro_message, speak=True)
        st.session_state.messages.append(intro_message)

    else:
        # Display chat messages from history on app rerun
        process_chat_history(st.session_state.messages)



    # Displaying chat messages
    # TODO:
    # display_chat(chat_messages)



    with bottom():
        st.markdown(f"""
        <p style='line-height: 0; font-size: 14px; text-align: center; color: #9c9d9f;'>Civic Sage can make mistakes. Always verify important information.</p>
        """, unsafe_allow_html=True)
        prompt = st.chat_input(f"Enter a question regarding {mp_name}")
        


    # for message in st.session_state.messages:
    #     with st.chat_message(message["role"]):
    #         st.markdown(message["content"])


    if prompt:
        # with st.chat_message("user"):
        #     st.write(prompt)

    # React to user input
    # if prompt := st.chat_input("What is up?"):
        # Display user message in chat message container & # Add user message to chat history
        send_chat_message({"role": "user", "message": {"content": prompt}})
        # st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "date": datetime.now().strftime("%d/%m/%Y"), "time": datetime.now().strftime("%H:%M:%S"), "message": {"content": prompt}})

        response = f"Echo: {prompt}"
        # Display assistant response in chat message container & chat history
        # st.chat_message("assistant").markdown(response)

        with st.spinner("Retrieving info..."):
            response = gpt_utils.prompt(prompt)
            time.sleep(2)

        send_chat_message({"role": "ai", "message": {"content": response}}, speak=True)
        st.session_state.messages.append({"role": "ai", "date": datetime.now().strftime("%d/%m/%Y"), "time": datetime.now().strftime("%H:%M:%S"), "message": {"content": response}})



