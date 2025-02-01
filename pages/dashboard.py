import streamlit as st
import utils.streamlit_utils as st_utils
import utils.constants as constants
import pandas as pd

st_utils.create_page_setup(page_name="Dashboard")

st.write("https://blog.streamlit.io/streamlit-authenticator-part-1-adding-an-authentication-component-to-your-app/")



for file in constants.PATH_CONVERSATIONS.iterdir():
    st.table(pd.read_csv(file))



