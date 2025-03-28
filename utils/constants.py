from pathlib import Path
from dotenv import load_dotenv
import os

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
PASSWORD_DASHBOARD = os.getenv("DASHBOARD_PASSWORD")

