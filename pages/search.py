import streamlit as st
import utils.streamlit_utils as st_utils

import utils.constants as constants

st_utils.create_page_setup(page_name="Search")

st.title("Search for an MP")




from streamlit_searchbox import st_searchbox
def search(searchterm: str):
    return ["Sir Keir Starmer"]

st.markdown("<p style='line-height: 0; font-size: 15px;'>Search for a Member of Parliament (MP) or Constituency</p>",  unsafe_allow_html=True)
selected_value = st_searchbox(
    search,
    placeholder="...",
    key="my_key",
)

# mp_choice = st.selectbox(
#     label="Select a Member of Parliament (MP)",
#     options=["Sir Keir Starmer", "Rishi Sunak", "Liz Truss", "Boris Johnson", "Theresa May"],
# )

mp_choice = "Sir Keir Starmer"

mp_constituency = "Holborn and St Pancras"
mp_service = "7 May 2015 - Present"

from PIL import Image
col1, col2 = st.columns([1, 3], gap="small")


image = Image.open(f"{constants.PATH_IMAGES}/Portrait.jpg")

with col1:
    border_size = 100
    new_height = image.height + border_size
    new_image = Image.new('RGB', (image.width, new_height), "#e4003b")
    new_image.paste(image, (0, 0))  # Paste the original image

    st.image(new_image, width=150, caption=f"{mp_choice} © House of Commons")

with col2:
    st.markdown(f"""
                <p style='line-height: 1; font-size: 28px; font-weight: bold;'>{mp_choice}</p>
                <p style='line-height: 0; font-size: 20px;'>Member of Parliament for <b>{mp_constituency}</b></p>
                <p style='line-height: 0.8; font-size: 16px;'>{mp_service}</p>

                <p style='font-size: 20px; color: #e4003b;'>Labour Party</p>
                """, unsafe_allow_html=True)
    
    with st.expander(f"Find {mp_choice} online"):
        sub_col_1, sub_col_2, sub_col_3 = st.columns([1, 1, 1], gap="small")
        with sub_col_1:
            st.button("X (@keir_starmer) 🡭")
        
        with sub_col_2:
            st.button("Constituency Office 🡭")

        with sub_col_3:
            st.button("Parliamentary Office 🡭")

    with st.expander(f"See {mp_choice}'s political career history"):
        st.write("1")

st.divider()


# pass search function and other options as needed


def format_ai_response(message):
    return f"""
        <div style="display: flex; margin-top: 10px;">
            <p style='font-size: 18px; line-height: 0px; color: {st_utils.THEMES_MAIN};'><b>Civic Sage</b></p>
            {"<p style='font-size: 14px; line-height: 0px;'>&nbsp;&nbsp;&nbsp; • &nbsp;&nbsp; Data as of Jan, 2017</p>" if "sources" in message else ""}
        </div>

        <p style='font-size: 16px; line-height: 18px;'>{message["content"]}</p>
    """


def display_chat(messages):
    for message in messages:
        with st.chat_message(message["role"]):
            # AI text
            if message["role"] == "ai":
                st.markdown(format_ai_response(message["message"]), unsafe_allow_html=True)

                if "sources" in message["message"]:
                    with st.expander("🔍 Sources"):
                        st.markdown(message["message"]["sources"], unsafe_allow_html=True)

            else:
                st.write(message["message"]["content"])




chat_messages = [
    {"role": "ai", "message": {"content": f"Hi there! Feel free to ask me to explain any political information about {mp_choice}!"}},
    {"role": "user", "message": {"content": "What did they vote for on the assisted dying bill?"}},
    {"role": "ai", "message": {
        "content": "Sir Keir Starmer voted 'Aye' (yes) on the Terminally Ill Adults (End of Life) Bill: Second Reading on 29 November 2024. It subsequently passed with 330 (Ayes) to 275 (Noes) <a href='https://google.com'>[1]</a>",
        "sources": "<a href='https://google.com' style='font-size: 18px'><b>[1]</b></a>: Test bla bla bla",
        }
    },
]

# Displaying chat messages
display_chat(chat_messages)

# with st.chat_message(assistant_name):
#     st.write("Hello human")
#     st.bar_chart(np.random.randn(30, 3))


from streamlit_extras.bottom_container import bottom 

with bottom():
    st.markdown(f"""
    <p style='line-height: 0; font-size: 14px; text-align: center; color: #9c9d9f;'>Civic Sage can make mistakes. Always verify important information.</p>
    """, unsafe_allow_html=True)
    prompt = st.chat_input(f"Enter a question regarding {mp_choice}")
    
if prompt:
    with st.chat_message("user"):
        st.write(prompt)
