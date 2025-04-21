


# Search
1. Display initial UI / searchbox to select an MP
2. READ info from database into Streamlit on selected MP and display UI elements
3. Send Conversation UI intro message


?. When user either uses prompt search OR clicks a pre-made search suggestion button
- Send prompt to LLM, and pair with pre-defined LLM settings + the system prompt + conversation history
- LLM:
  - Searches database with RAG to compile response information
  - If cant find from DB, searches the internet (and applies massive warning to info received)
  - If still cant find info, provides a pre-defined cant find message.




? RAG
- Traditionally, LLMs have 2 important weaknesses:
  - Static world knowledge (LLMs are trained on data up to a certain date for when that model is trained, older models = older timeframes)
  - Lack of specialised info (LLMs are trained on massive, massive corpuses of datasets. So very good at general knowledge, but subject-specific-niches not so good).
- RAG is the answer to these 2 problems. RAG does:
- Augmenting LLM with specialised and mutable (updatable) knowledge base
https://i.imgur.com/vgHo37p.png

Retrieving correct data from our knowledgebase is done by:
Retriever:
- Text embeddings (usually)
  - Numbers that represent the meaning within a set of text
  - e.g. we have a collection of words (tree, daisy, sattelite, spaceship, basketball)
  - Text embeddings are a set of numbers associated with each word to show the 'meaning' of the text, plotted on an axis so similar concepts are close together.
    https://i.imgur.com/i2Hx0zs.png

    Text Embedding-based Search
    - So we represent these as 'points' in the graph.
    - We make our search query, and plot its own numbers.
    - We retrieve the closest records.
    https://i.imgur.com/Fr3fAyL.png


Knowledgebase (e.g. a large stack of documents):
- First we need to take the raw files and turn into a knowledge base:
    1. Load the documents (get them all together, get them into a ready-to-parse format). For us, JSON? It needs to be in text. Is JSON acceptable?
    2. Chunk documents: LLMs have a 'fixed context window' so we cant just dump them all into prompt. We have to split it into smaller pieces. even if you have a giant model, better performance.
    3. Embed the chunks: Take the chunk and translate it into a 'vector' / 'set of numbers' that is the embedding location
    4. For each embedding-translated-chunk, load into a Vector DB: Where we then do a text-based embedding search
https://www.youtube.com/watch?v=Ylz779Op9Pw


?. When leaving page / switching to another MP via searchbox - if conversation history exists, and more than 1 message sent:
- compile conversation as Pandas DataFrame and save as .csv
- Anonymise somewhere?
- Store to database