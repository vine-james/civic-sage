from pathlib import Path
from dotenv import load_dotenv
import os
from enum import Enum
import streamlit as st


# Paths
CWD = Path.cwd()
PATH_FILES = CWD / "files"
PATH_IMAGES = PATH_FILES / "images"
PATH_CONVERSATIONS = PATH_FILES / "conversations"
PATH_PDFS = PATH_FILES / "pdfs"

# Tokens
load_dotenv() # NOTE: load_dotenv() replaced with streamlit secrets as I am now deploying the app on Streamlit Community Cloud.

def get_secret(key, deployed=True):
    if deployed:
        return st.secrets[key]
    else:
        return os.getenv(key)

TOKEN_GITHUB = get_secret("GITHUB_REPO_TOKEN")
TOKEN_OPENAI = get_secret("OPENAI_TOKEN")
TOKEN_PINECONE = get_secret("PINECONE_TOKEN")
TOKEN_THEYWORKFORYOU = get_secret("THEYWORKFORYOU_TOKEN")

TOKEN_AWS_ACCESS = get_secret("AWS_ACCESS_KEY")
TOKEN_AWS_SECRET = get_secret("AWS_SECRET_KEY")

AWS_REGION = get_secret("AWS_REGION")
AWS_URL_ANALYSE_FUNCTION = get_secret("ANALYSE_FUNCTION_URL")

PASSWORD_DASHBOARD = get_secret("DASHBOARD_PASSWORD")


# Misc
# Have to put this in here as can't be in plot_utils due to circular invocation
class ChartTypes(Enum):
    LINE = "line"
    BAR = "bar"
    OTHER = "other"
    CHOROPLETH = "choropleth"
    SCATTER = "scatter"
    