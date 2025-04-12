import streamlit as st
import utils.streamlit_utils as st_utils
import utils.gpt_utils as gpt_utils
import time
import pandas as pd
from datetime import datetime
from streamlit_extras.bottom_container import bottom 

import utils.constants as constants

st_utils.create_page_setup(page_name="Search")


from collections import namedtuple
MP_Data = namedtuple("MP_Data", ["Portrait", "Party", "Constituency", "Tenure", "Contact", "History"])

# Store the currently selected MP dropdown box value, so that each run, if old is different to new, reset the chat history (cant figure out another way to do this)
current_selected_mp = None
if "current_selected_mp" not in st.session_state:
    st.session_state.current_selected_mp = None


if "messages" not in st.session_state:
    st.session_state.messages = []


if "usage_agreement" not in st.session_state:
    st.session_state.usage_agreement = False


@st.dialog("Civic Sage Usage Agreement")
def usage_agreement():

    # May need to refine these questions or base them off something more concrete.
    # Q1 and 2 are based on Hansard Society's form, but Q3 is something I just pulled out to match.
    # Scales are also not backed up by anything academic.

    st.write("**Please rate**: How much, if anything do you feel you know about:")

    select_options = ["Nothing at all", "Not very much", "A fair amount", "A great deal"]

    user_knowledge_politics = st.select_slider("UK Politics", select_options)
    user_knowledge_parliament = st.select_slider("UK Parliament", select_options)
    user_knowledge_government = st.select_slider("UK Government", select_options, help="Confused about the difference between 'Parliament' and 'Government'? If so, please select the default 'Nothing at all'.")


    st.divider()

    st.write("""
    **Conditions of usage**:
             
    > While using Civic Sage, your prompts/messages/questions will be stored and personal information anonymised for group-wide analysis of sentiment and topics of interest. Your *individual* conversation will **NOT** be viewed. However, please do not include any private or sensitive information as part of your conversation.
    """)

    confirm = st.checkbox("**I agree to the conditions set out above while using Civic Sage.**")

    submit = st.button("Continue", disabled=not confirm)
    if submit:
        st.session_state.usage_agreement = True
        st.session_state.user_knowledge_politics = user_knowledge_politics
        st.session_state.user_knowledge_politics = user_knowledge_parliament
        st.session_state.user_knowledge_politics = user_knowledge_government

        st.rerun()

if st.session_state.usage_agreement == False:
    usage_agreement()
else:
    # Visual confirmation of submission
    st.info("Successful Authentication | You have agreed to the Civic Sage Usage Agreement", icon=":material/check_box:")



st.info("Need to include a thing where, when selecting MP, if yours isnt there, heres a list of other MPs:")

st.title("Search for an MP")
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


st.info("NEED TO TURN OFF CHATGPT OPTIOON FOR SHARING PROMPTS FOR EXTRA TOKENS BEFORE DEPLYOING TO PROD")
st.info("Contains Parliamentary information licensed under the Open Parliament Licence v3.0.")



parties_main_theme = {
    "Conservative": "#0087dc",
    "Labour": "#e4003b",
    "Liberal Democrats": "#FDBB30",
    "Reform UK": 4,
}

@st.dialog("Report a mistake in a Civic Sage response")
def report(message, tree):
    # st.write("Response:")
    # st.write(message["content"])


    if not st.button("Submit"):
        st.write(":material/speaker_notes_off: Reported Response:")
        block_col, reported_response = st.columns([1, 20])
        with block_col:
            st.markdown("""
            <div style="background-color: #808080; width: 40%; height: 1000%;">
            </div>
            """, unsafe_allow_html=True)
        with reported_response:
            st.caption(message["content"])

        st.divider()

        # TODO: Make sure when reporting to report the entire conversation in the logs (but only show the message, as we need to know how the conversation got to this point)

        reported_tags = st.pills(":material/label: How would you tag the response error? [Multi-select]", ["Inaccurate information", "Inaccurate sources", "Political bias", "Explanation not understandable", "Other"], selection_mode="multi")

        st.text_area(
            ":material/rate_review: Enter any additional comments below:",
            ""
        )
        # if password_input == constants.PASSWORD_DASHBOARD:
        #     st.session_state.authenticated = True
        #     st.rerun()
    else:
        st.success("**Report submitted successfully**\n\nThank you for your feedback!\nThis information will be assessed by a human reviewer. In the meantime, we have flagged this response within the conversation history to ensure proper conversation clarity.", icon=":material/task_alt:")
        dismiss_bar = st.progress(0, text=None)
        time_to_read = 6 # Seconds

        for percent_complete in range(100):
            time.sleep(time_to_read / 100)
            dismiss_bar.progress(percent_complete + 1, text=None)
        time.sleep(1)
        st.rerun()
        
        # else:
        #     st.error("Password incorrect")
    
    # with st.form("my_form"):
    #     st.write("Inside the form")
    #     my_number = st.slider('Pick a number', 1, 10)
    #     my_color = st.selectbox('Pick a color', ['red','orange','green','blue','violet'])
    #     st.form_submit_button('Submit my picks')



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
                col_1, col_2 = st.columns([5, 1])
                with col_1:
                    with st.expander("Sources", icon=":material/find_in_page:"):
                        st.markdown(message["message"]["sources"], unsafe_allow_html=True)

                with col_2:
                    st.button("", icon=":material/thumb_down:", help="Spotted a mistake in Civic Sage's response? Click me to report the message.", on_click=report, args=(message["message"], 2))
        


                    
                
        

                    

                

        else:
            st.write(message["message"]["content"])

def process_chat_history(messages):
    # for i, message in enumerate(messages):
    for message in messages:
        send_chat_message(message)
        



def process_prompt_and_response(prompt):
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



from streamlit_searchbox import st_searchbox
def search(searchterm: str):
    return ["Keir Starmer", "Paul Holmes"]

st.markdown("<p style='line-height: 0; font-size: 15px;'>Search for a Member of Parliament (MP) or Constituency</p>",  unsafe_allow_html=True)
mp_name = st_searchbox(
    search,
    placeholder="Search for an MP",
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
        
        with st.expander(f"Find {mp_name} online", icon=":material/share:"):
            cols = st.columns([1 for _ in mp_data.Contact], gap="small")
            
            for col, contact_dict in zip(cols, mp_data.Contact.items()):
                with col:
                    st.link_button(f"{contact_dict[0]} :material/arrow_outward:", contact_dict[1])

        with st.expander(f"See {mp_name}'s political career history", icon=":material/id_card:"):
            tab_elections, tab_gov, tab_opposition, tab_committees = st.tabs([":material/how_to_vote: Elections", ":material/account_balance: Gov Posts", ":material/mystery: Opposition Posts", ":material/adaptive_audio_mic: Committees"])
            cols = st.columns([1, 5])
            with cols[0]:
                st.write(":material/radio_button_checked:")

            with cols[1]:
                st.write("Test<br>Test2")
            st.markdown("""
                <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
            """, unsafe_allow_html=True)


            

            st.markdown(f"""
                <span><i class="material-icons" style="font-size: 20px; color: {st_utils.THEMES_MAIN};">radio_button_checked</i> <span style='font-size: 18px;'><b>Test</b></span><br><span style='font-size: 14px;'>Tes 2</span></span>
                <br>
                <i class="material-icons" style="font-size: 16px; color: {st_utils.THEMES_MAIN};">more_vert</i>
                <br>
                <span><i class="material-icons" style="font-size: 16px; color: {st_utils.THEMES_MAIN};">radio_button_unchecked</i> <b>Test</b></span>
                <br>
                <i class="material-icons" style="font-size: 16px; color: {st_utils.THEMES_MAIN};">more_vert</i>
                <br>
                <span><i class="material-icons" style="font-size: 16px; color: {st_utils.THEMES_MAIN};">radio_button_unchecked</i> <b>Test</b></span>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div style="position: relative; width: 200px; padding: 20px;">
                        
                <span><i class="material-icons" style="font-size: 16px; color: red;">check</i> <p>Test</p></span>
                <!-- Timeline Line -->
                <div style="position: absolute; top: 40px; left: 15px; bottom: 0; width: 3px; background-color: red;"></div>

                <!-- First timeline item -->
                <div style="display: flex; align-items: center; margin-bottom: 40px; position: relative;">
                    <div style="width: 30px; height: 30px; border: 3px solid red; border-radius: 50%; background: white; position: absolute; left: 0;"></div>
                    <div style="margin-left: 50px; color: black; text-shadow: 1px 1px 0px white;">
                        <div style="font-size: 16px; font-weight: bold;">Text1</div>
                        <div style="font-size: 14px;">Subtext1</div>
                    </div>
                </div>

                <!-- Second timeline item -->
                <div style="display: flex; align-items: center; margin-bottom: 40px; position: relative;">
                    <div style="width: 30px; height: 30px; border: 3px solid red; border-radius: 50%; background: white; position: absolute; left: 0;"></div>
                    <div style="margin-left: 50px; color: black; text-shadow: 1px 1px 0px white;">
                        <div style="font-size: 16px; font-weight: bold;">Text2</div>
                        <div style="font-size: 14px;">Subtext2</div>
                    </div>
                </div>

            </div>
            """, unsafe_allow_html=True)
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
        st_utils.save_conversation_to_csv()
        st.session_state.current_selected_mp = mp_name

        # Set up intro message
        intro_message = {"role": "ai", "date": datetime.now().strftime("%d/%m/%Y"), "time": datetime.now().strftime("%H:%M:%S"), "message": {"content": f"Hi there! Feel free to ask me to explain any political information about {mp_name}!"}}
        send_chat_message(intro_message, speak=True)
        st.session_state.messages.append(intro_message)

        msg = {"role": "ai",
         "message": {
            "content": "Sir Keir Starmer voted 'Aye' (yes) on the Terminally Ill Adults (End of Life) Bill: Second Reading on 29 November 2024. It subsequently passed with 330 (Ayes) to 275 (Noes) [[1]](https://google.com)",
            "sources": "<a href='https://google.com' style='font-size: 18px'><b>[1]</b></a>: Test bla bla bla",
            }
        }
        send_chat_message(msg, speak=True)

    else:
        # Display chat messages from history on app rerun
        process_chat_history(st.session_state.messages)



    # Displaying chat messages
    # TODO:
    # display_chat(chat_messages)

    if "button_pressed" not in st.session_state:
        st.session_state["button_pressed"] = False
        st.session_state["current_prompt"] = None

    with bottom():


        st.markdown(f"""
        <p style='line-height: 0; font-size: 14px; text-align: center; color: #9c9d9f;'>Civic Sage can make mistakes. Always verify important information.</p>
        """, unsafe_allow_html=True)

        bottom_col_1, bottom_col_2 = st.columns([1, 7])

        with bottom_col_1:
            with st.popover("", icon=":material/help:", help="Select from a list of sample questions"):
                suggested_prompts = [f"What is {mp_name}'s recent voting record?", f"What declared payments has {mp_name} received?", f"When was {mp_name} elected?"]
                button_cols = st.columns([1 for _ in suggested_prompts])

                for i, button_col in enumerate(button_cols):
                    with button_col:
                        if st.button(f":material/search: {suggested_prompts[i]}"):
                            st.session_state["current_prompt"] = suggested_prompts[i]
                            st.session_state["button_pressed"] = True

                # TODO: Reminder of sample prompts could style around
                st.image(constants.PATH_IMAGES / "temp-to-remind-sample-prompts.png")


        with bottom_col_2:
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
        process_prompt_and_response(prompt)

    if st.session_state["button_pressed"]:
        process_prompt_and_response(st.session_state["current_prompt"])
        st.session_state["current_prompt"] = ""
        st.session_state["button_pressed"] = False  # Reset after handling



        



