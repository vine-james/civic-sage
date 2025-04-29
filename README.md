
<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="files/images/civic-sage-banner.png" width="700px">
    <img alt="Civic Sage Banner" src="files/images/civic-sage-banner.png" width="600px">
  </picture>
</div>

# 🗳️ **Civic Sage** 

**[Civic Sage](https://civicsage.streamlit.app/)** aims to make information on UK Members of Parliament (MPs) easier to understand and more accessible. By programmatically collecting extensive 'profile' knowledge bases, pairing them with a RAG-LLM pipeline, users can retrieve factual, easy-to-digest information about a selected MP.

Additionally, Civic Sage analyses anonymised conversations at scale, generating group-level insights into user engagement per specific MP — aspiring to helping both citizens and representatives connect better online.

This product was created in partial completion of my Bournemouth University BSc Dissertation.


## Deployment

> To view Civic Sage deployed, please visit the [Civic Sage website](https://civicsage.streamlit.app/).



## Usage
> [!IMPORTANT]  
> Before using any of the commands below, ensure you have:
> 1. Installed (e.g. `pip install -r requirements.txt`) the required dependencies into (and activated) a virtual environment.
> 2. Provisioned your own copies of the necessary infastructure (and thus, their subsequent secrets/tokens) into a `.env` file. Consult [constants.py](utils/constants.py) to determine required items.

| Command | Description |
| --- | --- |
| `streamlit run streamlit_app.py` | Run a local version of Civic Sage. |
| `pytest` or `pytest -v` | Run Civic Sage's unit tests. |
| `python -m files.meta_evaluation.evaluation` | Run Civic Sage's 'intelligent' LLM-driven tests. |



