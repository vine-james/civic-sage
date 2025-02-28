import streamlit as st
import utils.streamlit_utils as st_utils
import utils.constants as constants

from streamlit_extras.mention import mention
from streamlit_extras.add_vertical_space import add_vertical_space 

st_utils.create_page_setup(page_name="Home")
# st.image(st_utils.get_themed_icon(constants.PATH_IMAGES / "CivicSage-Banner-A-1.png"))
# st.image(st_utils.get_themed_icon(constants.PATH_IMAGES / "CivicSage-Banner-A-2.png"))

# st.image(st_utils.get_themed_icon(constants.PATH_IMAGES / "CivicSage-Banner-B-1.png"))
# st.image(st_utils.get_themed_icon(constants.PATH_IMAGES / "CivicSage-Banner-B-2.png"))

# st.image(st_utils.get_themed_icon(constants.PATH_IMAGES / "CivicSage-Banner-C-1.png"))

st.image(st_utils.get_themed_icon(constants.PATH_IMAGES / "CivicSage-Banner-D-1.png"))
st.image(st_utils.get_themed_icon(constants.PATH_IMAGES / "CivicSage-Banner-D-2.png"))
st.image(st_utils.get_themed_icon(constants.PATH_IMAGES / "civic-sage-banner.png"))




columns = st.columns([1, 1, 2])
with columns[0]:
    if st.button(":material/search: Search for an MP"):
        st.switch_page("pages/search.py")

with columns[1]:
    if st.button(":material/view_kanban: View Dashboard"):
        st.switch_page("pages/dashboard.py")

add_vertical_space(2)


st.write("""Civic Sage makes politics easier to understand and more accessible. Our platform lets you ask questions and get factual, easy-to-digest information about your local Members of Parliament (MP). Whether you’re curious about what they’ve done, what they stand for, or how they’re representing you, Civic Sage gives you clear and trustworthy answers. Empower yourself with knowledge and engage confidently in your democracy.""")

st.write("Civic Sage analyses anonymises conversations and analyses them as a group to provide insights into what matters most to people in your area — helping both citizens and representatives connect better.")

st.divider()

st.write("This product was created in partial completion of my Bournemouth University BSc Dissertation. Code is accessible via GitHub, deployed with [Streamlit Community Cloud](https://streamlit.io/cloud) and data is stored/read from an [Amazon Relational Database](https://aws.amazon.com/rds/).")
         
        
st.write("You can access the code, or connect with me here:")

col_1, col_2, col_3, _ = st.columns([0.2, 0.16, 0.25, 0.25])
with col_1:
    mention(label="Connect with me",
            icon="👤",
            url="https://www.linkedin.com/in/j-vine/")

with col_2:
    mention(label="GitHub Repo",
            icon="github",
            url="https://github.com/vine-james/civic-sage")

with col_3:
    mention(label="Hosted Webserver",
            icon="streamlit",
            url="https://civicsage.streamlit.app/")
