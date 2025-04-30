import streamlit as st
import utils.streamlit_utils as st_utils
import utils.constants as constants

from streamlit_extras.mention import mention
from streamlit_extras.add_vertical_space import add_vertical_space 

st_utils.create_page_setup(page_name="Home")
st.image(constants.PATH_IMAGES / "civic-sage-banner.png")


columns = st.columns([1, 1, 2])
with columns[0]:
    if st.button(":material/search: Search for an MP"):
        st.switch_page("pages/search.py")

with columns[1]:
    if st.button(":material/view_kanban: View Dashboard"):
        st.switch_page("pages/dashboard.py")

add_vertical_space(2)

st.markdown(
    "<link href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css' rel='stylesheet'>",
    unsafe_allow_html=True
)

st.write("""
    Civic Sage aims to make UK parliamentary politics easier to understand and more accessible.

    Whether you’re curious about what a Member of Parliament (MP) stands for, or how your local MP represents you, Civic Sage allows you to ask questions and receive factual, easy-to-digest responses.
    
    Civic Sage analyses anonymised conversations at scale, generating group-level insights into user engagement per specific MP — aspiring to helping both citizens and representatives connect better online.

    ---

    This product was created in partial completion of my Bournemouth University BSc Dissertation. Code is accessible via GitHub, deployed with [Streamlit Cloud](https://streamlit.io/cloud) and each data pipeline is handled within [Pinecone](https://www.pinecone.io/), AWS [DynamoDB](https://aws.amazon.com/dynamodb/), [S3](https://aws.amazon.com/s3/), [Lambda](https://aws.amazon.com/lambda/) & [ECR](https://aws.amazon.com/ecr/).
    
    Some key (but not all) packages/software used are: [Streamlit](https://streamlit.io/), [LangChain](https://www.langchain.com/), [Pandas](https://pandas.pydata.org/) / [Geopandas](https://geopandas.org/en/stable/), [Plotly](https://plotly.com/), [Docker](https://www.docker.com/), [Presidio](https://microsoft.github.io/presidio/) and Laurer et al.'s DeBERTa zero-shot NLI model [[^1]](https://huggingface.co/MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli) [[^2]](https://osf.io/74b8k).

    You can access the code, or connect with me here:
""")

cols = st.columns([0.22, 0.18, 0.18, 0.24, 0.2])
with cols[0]:
    mention(label="Connect with me",
            icon="<i class='fa-brands fa-linkedin'></i>",
            url="https://www.linkedin.com/in/j-vine/")
    
with cols[1]:
    mention(label="Get in touch",
            icon="<i class='fa-solid fa-envelope'></i>",
            url="mailto:james@jvine.uk")

with cols[2]:
    mention(label="GitHub Repo",
            icon="github",
            url="https://github.com/vine-james/civic-sage")

with cols[3]:
    mention(label="Hosted Webserver",
            icon="streamlit",
            url="https://civicsage.streamlit.app/")
