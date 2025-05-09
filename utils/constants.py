from pathlib import Path
from dotenv import load_dotenv
import os
from enum import Enum
import streamlit as st
import platform

# Paths
CWD = Path.cwd()
PATH_FILES = CWD / "files"
PATH_IMAGES = PATH_FILES / "images"
PATH_CONVERSATIONS = PATH_FILES / "conversations"
PATH_PDFS = PATH_FILES / "pdfs"
PATH_MODELS = PATH_FILES / "models"

# Tokens
load_dotenv() # NOTE: load_dotenv() secrets have been replaced with streamlit secrets as I am now deploying the app on Streamlit Community Cloud.
IS_DEPLOYED = platform.processor() == ""

def get_secret(key, deployed=IS_DEPLOYED):
    if deployed:
        return st.secrets[key]
    else:
        return os.getenv(key)

TOKEN_GITHUB = get_secret("GITHUB_REPO_TOKEN") # Token for the GitHub repo (to show current version release.)
TOKEN_OPENAI = get_secret("OPENAI_TOKEN") # Token for OpenAI (LLM.)
TOKEN_PINECONE = get_secret("PINECONE_TOKEN") # Token for Pinecone vector database.
TOKEN_THEYWORKFORYOU = get_secret("THEYWORKFORYOU_TOKEN") # Token for TheyWorkForYou's API.

TOKEN_AWS_ACCESS = get_secret("AWS_ACCESS_KEY") # Token for AWS infastructure access key.
TOKEN_AWS_SECRET = get_secret("AWS_SECRET_KEY") # Token for AWS infastructure secret access key.

AWS_REGION = get_secret("AWS_REGION") # The chosen AWS infastructure region.
AWS_URL_ANALYSE_FUNCTION = get_secret("ANALYSE_FUNCTION_URL") # A internal function URL to manually activate an AWS Lambda function.

PASSWORD_DASHBOARD = get_secret("DASHBOARD_PASSWORD") # The password for the dashboard page.


# Misc
# Have to put this in here as can't be in plot_utils due to circular invocation
class ChartTypes(Enum):
    LINE = "line"
    BAR = "bar"
    OTHER = "other"
    CHOROPLETH = "choropleth"
    SCATTER = "scatter"
    