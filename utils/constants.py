from pathlib import Path
from dotenv import load_dotenv
import os
from enum import Enum


# Paths
CWD = Path.cwd()
PATH_FILES = CWD / "files"
PATH_IMAGES = PATH_FILES / "images"
PATH_CONVERSATIONS = PATH_FILES / "conversations"
PATH_PDFS = PATH_FILES / "pdfs"

# Tokens
load_dotenv()

TOKEN_GITHUB = os.getenv("GITHUB_REPO_TOKEN")
TOKEN_OPENAI = os.getenv("OPENAI_TOKEN")
TOKEN_PINECONE = os.getenv("PINECONE_TOKEN")
TOKEN_THEYWORKFORYOU = os.getenv("THEYWORKFORYOU_TOKEN")

TOKEN_AWS_ACCESS = os.getenv("AWS_ACCESS_KEY")
TOKEN_AWS_SECRET = os.getenv("AWS_SECRET_KEY")

AWS_REGION = os.getenv("AWS_REGION")
AWS_URL_ANALYSE_FUNCTION = os.getenv("ANALYSE_FUNCTION_URL")

PASSWORD_DASHBOARD = os.getenv("DASHBOARD_PASSWORD")


# Misc
# Have to put this in here as can't be in plot_utils due to circular invocation
class ChartTypes(Enum):
    LINE = "line"
    BAR = "bar"
    OTHER = "other"
    CHOROPLETH = "choropleth"
    SCATTER = "scatter"
    