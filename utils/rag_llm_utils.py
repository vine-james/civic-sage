from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_pinecone import PineconeVectorStore
from langchain_core.runnables import RunnablePassthrough
from pinecone import Pinecone, ServerlessSpec
from functools import partial
from datetime import datetime

import utils.constants as constants

index_name = "mp-data"
pc = Pinecone(api_key=constants.TOKEN_PINECONE)

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1",
        )
    )

dense_index = pc.Index(index_name)

embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", api_key=constants.TOKEN_OPENAI)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=constants.TOKEN_OPENAI,
)

llm_with_tools = llm.bind_tools([{"type": "web_search_preview"}])

prompt_template_summarise_history = SystemMessagePromptTemplate.from_template(
    "Your job is to take in a list of chat messages that make up the chat history of you and the user. Summarise the discussion as if you need to remember the key points."
)

summarise_template = ChatPromptTemplate.from_messages(
    [
        prompt_template_summarise_history,
        ("human", "{user_input}")
    ]
)


class ChatHistory:
    def __init__(self, size: int):
        self.size = size
        self.message_window = []
        self.all_messages = []
        self.current_message_index = 0

    def add_message(self, message: str):
        if len(self.message_window) >= self.size:
            self.message_window.pop(0)
        
        self.current_message_index += 1
        self.message_window.append({"message": message, "time": datetime.now(), "message_index": self.current_message_index})
        
        # Add in to history of all messages (for non-LLM comptuation)
        self.all_messages.append({"message": message, "time": datetime.now(), "message_index": self.current_message_index})

    def get_last_message(self):
        # Doesn't need time as the methods we're using it for only need the actual question content
        return self.message_window[-1]

    # Internal function
    def _format_messages(self, messages):
        chat_str = ""

        for chat_message in messages:
            if isinstance(chat_message["message"], HumanMessage):
                chat_str += f"\nHuman: {chat_message['message'].content}"
            elif isinstance(chat_message["message"], AIMessage):
                chat_str += f"\nAssistant: {chat_message['message'].content}"
            elif isinstance(chat_message['message'], SystemMessage):
                chat_str += f" \nSystem: {chat_message['message'].content}"

        return chat_str

    def get_message_window_formatted(self, _=None):
        return {"user_input": self._format_messages(self.message_window)}
    
    # Get a list of all the raw messages from a specific author (either user or AI/assistant)
    def get_author_messages(self, author):
        author_type = {"Human": HumanMessage, "Assistant": AIMessage, "System": SystemMessage}
        return [message["message"] for message in self.all_messages if isinstance(message["message"], author_type[author])]
    
    def get_reported_message_context(self, reported_message_index):
        # 5 previous messages
        start_index = max(0, reported_message_index - 6)
        
        return [message["message"].content for message in self.all_messages[start_index : reported_message_index - 1]]


class User:
    def __init__(self, competencies: dict):
        self.competencies = {
            "UK Politics": competencies["UK Politics"],
            "UK Parliament": competencies["UK Parliament"],
            "UK Government": competencies["UK Government"],
        }

        self.competence_max_rating = 4
        
    def get_numerical_score(self, competency):
        levels = {
            "Nothing at all": 1, 
            "Not very much": 2, 
            "A fair amount": 3,
            "A great deal": 4,
        }
        
        return levels[competency]

    def get_competencies_plaintext(self):
        competencies_str = ""

        for name, rating in self.competencies.items():
            competencies_str+= f"{name}: {rating} ({self.get_numerical_score(rating)}/{self.competence_max_rating})\n"

        competencies_str += f"Competency Scale: [1 (lowest) - {self.competence_max_rating} (highest)]"

        return competencies_str


# Temporary set-up of chat history & vector store which is then replaced when module initialised with session-based chat history.
chat_history = ChatHistory(size=20)
def init(ch):
    global chat_history
    chat_history = ch

    return chat_history


chain_summarise_history = chat_history.get_message_window_formatted | summarise_template | llm


prompt_template = ChatPromptTemplate.from_messages(
    [
        SystemMessage(
            # NOTE: Now added few-shot prompting examples to the PERSONAL and SENSITIVE classifications as well as basic concluding 'chain-of-thought' instruction + few-shot example.
            content="""
            Your name is Civic Sage. You are designed to helpfully answer questions about UK politics, government and parliament. Answer questions based on the context provided. 

            - ALWAYS provide URL sources if possible, included after the relevant statement on the same text line, formatted as "[SOURCE URL: URL HERE]".

            - Please tailor your answers based on the users self-described expertise in the subjects mentioned, making sure they fit their level of understanding.

            - Provide an impartial and balanced answer, avoiding personal opinion or value judgments. Consider perspectives from multiple sides where relevant.

            - Try to keep the topic of conversation about UK politics, government and parliament.

            - If the question received is overly sensitive or personal to the user, say exactly "PERSONAL" and nothing else, for example:
                User: "Can the MP help me sort out my finances?"
                AI: "PERSONAL"

                User: "Can the MP help me call an ambulance?"
                AI: "PERSONAL"

            - If you don't know the answer, say exactly "UNKNOWN" and nothing else, for example:
                User: "Whats the latest on Donald Trump?"
                AI: "UNKNOWN"

                User: "How tall is Big Ben?"
                AI: "UNKNOWN

            - For complex or reasoning questions, explain your reasoning step by step before giving the final answer, for example:
                User: Why did the MP vote against the bill?
                AI: To answer, I'll check the MP's voting record, public statements, and any debate contributions. The MP voted against the bill [SOURCE URL:...]. In the debate, she expressed concerns about funding allocations [SOURCE URL:...]. Her official statement cited local constituent feedback as a factor [SOURCE URL:...]. Therefore, the MP's reasons appear to be funding concerns and constituent input.
                
            """
        ),
        ("human", "Todays date: {date}"),
        ("human", "User self-described expertise: {user_competency}"),
        ("human", "Chat history summary: {history}"),
        ("human", "Context: {context}"),
        ("human", "{question}"),
    ]
)


def summarize_history(input_):
    # First, summarize the chat history
    summary_chain = chat_history.get_message_window_formatted | summarise_template | llm
    history_summary = summary_chain.invoke(None)
    
    return {
        "history": history_summary.content,
        "question": input_["question"],
        "user_competency": input_["user_competency"],
    }


def format_docs(docs):
    docs_done = "\n\n".join(f"---\nSource: {doc.metadata['data_source']}\n{doc.page_content}" for doc in docs)
    return docs_done


def check_and_search(result, retriever, mp_name, mp_constituency, date):
    # If result is an AIMessage, extract its content and the original question
    if hasattr(result, "content"):
        # If results are too personal, re-direct.
        if result.content.strip() == "PERSONAL":

            prompt_template_redirect_contact = ChatPromptTemplate.from_messages(
                [SystemMessage(
                    content="""
                        You've received a response which is overly sensitive or personal outside of the scope of your objectives. Your job is to re-direct the user to the appropriate contact services or their MP (only if its within their responsibilities) based on the context and original message provided below.
                        """
                    ),
                    ("human", "Context: {context}"),
                    ("human", "Original message: {message}"),
                ]
            )

            chain_redirect_contact = RunnablePassthrough.assign(
                context=RunnableLambda(lambda x: x["question"]) | retriever | format_docs 
            ) | prompt_template_redirect_contact | llm

            sensitive_reply = chain_redirect_contact.invoke({"question": "MP contact details", "message": chat_history.get_last_message()["message"].content})

            return f"SENSITIVE REPLY: \n___\n{sensitive_reply.content}"
        
        # If no relevant results found, conduct a websearch
        elif result.content.strip() == "UNKNOWN":
            # Try to get the original question from the additional context
            question = chat_history.get_last_message()["message"].content
            if question:
                try:
                    prompt_template_search = ChatPromptTemplate.from_messages(
                        [SystemMessage(
                            content="""
                            Your name is Civic Sage. You are designed to helpfully answer questions about UK politics, government and parliament. Your current focus is on the current-day Member of Parliament (MP) mentioned below.

                            Examine the original question below. If you can answer it, do so. If not, perform a web search to find the best results and explain the findings.

                            RULES:
                            - ALWAYS provide URL sources if possible, included after the relevant statement on the same text line, formatted as "[SOURCE URL: URL HERE].

                            - Keep your explanation brief, no more than 2 paragraphs worth of text.

                            - For complex or reasoning questions, explain your reasoning step by step before giving the final answer, for example:
                                User: Why did the MP vote against the bill?
                                AI: To answer, I'll check the MP's voting record, public statements, and any debate contributions. The MP voted against the bill [SOURCE URL:...]. In the debate, she expressed concerns about funding allocations [SOURCE URL:...]. Her official statement cited local constituent feedback as a factor [SOURCE URL:...]. Therefore, the MP's reasons appear to be funding concerns and constituent input.
                                
                            """
                            ),
                            ("human", "Todays date: {date}"),
                            ("human", "MP name: {mp_name}"),
                            ("human", "MP constituency: {mp_constituency}"),
                            ("human", "Original question: {question}"),
                            
                        ]
                    )

                    chain_web_search = prompt_template_search | llm_with_tools
                    search_results = chain_web_search.invoke({"question": question, "mp_name": mp_name, "mp_constituency": mp_constituency, "date": date})

                    # Check if the LLM actually performed a web search or just answered it by-itself and classify accordingly 
                    # (some responses are UNKNOWN) but don't require a web search
                    if search_results.additional_kwargs.get("tool_outputs"):
                        return f"WEB SEARCH: Unfortunately I couldn't generate an answer based on my internal data. Instead, here's what I found from searching the internet:\n___\n{search_results.content[0]['text']}"
                    else:
                        return search_results.content[0]["text"]

                except Exception as e:
                    return f"Error performing web search: {str(e)}"
            else:
                return "Unable to perform web search: No question found."
        
        # If not PERSONAL/UNKNOWN, question was successful, now run additional political-debiasing prompt
        # Try to get the original question from the additional context
        question = chat_history.get_last_message()["message"].content
        if question:
            prompt_template_political_bias = ChatPromptTemplate.from_messages(
                [SystemMessage(
                    content="""
                    Your name is Civic Sage. You are designed to helpfully answer questions about UK politics, government and parliament. Your current focus is on the current-day Member of Parliament (MP) labelled below.

                    Labelled below is an original text you generated.

                    Now rephrase your original text as needed, considering that you are an unbiased person whose priority is to present information impartially. 
                    If the question is potentially contentious, explicitly reference multiple viewpoints or major party perspectives, and include source URLs for verification. 
                    You do not discriminate or frame answers on the basis of political belief, gender, race, religion, or any other sensitive attribute.
                    
                    ALWAYS provide URL sources if possible, included after the relevant statement on the same text line, formatted as "[SOURCE URL: URL HERE].              

                    The original question is also labelled below.
                    """
                    ),
                    ("human", "Todays date: {date}"),
                    ("human", "MP name: {mp_name}"),
                    ("human", "Original text generated: {original_question}"),
                    ("human", "Original question: {question}"),
                ]
            )

            chain_political_debias = prompt_template_political_bias | llm
            results = chain_political_debias.invoke({"question": question, "original_question": result.content, "mp_name": mp_name, "date": date})
            
            return results.content
        
    
    # If result is not an AIMessage, return it as is
    return result


def safely_add_message(input):

    # If a dict, it is a question asked by user
    if type(input) == dict:
        try:
        # Add the human message to chat history
            chat_history.add_message(HumanMessage(content=input["question"]))
        except Exception as e:
            print(f"Error adding User message to history: {e}")
        return input


    # If a str, it is a formatted LLM response
    elif type(input) == str:
        try:
            chat_history.add_message(AIMessage(content=input))
        except Exception as e:
            print(f"Error adding AI message to history: {e}")
        return input
    
    else:
        print(f"Message couldn't be added to history, unexpected input: {input}")


def ask_prompt(question, user, mp_name, mp_constituency):
    vector_store = PineconeVectorStore(index=dense_index, embedding=embeddings, namespace=mp_name)

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5},
        text_key="data",
    )

    date_today = str(datetime.today())

    combined_chain = (
        RunnableLambda(safely_add_message)
        | RunnablePassthrough.assign(
            context=RunnableLambda(lambda x: x["question"]) | retriever | format_docs 
        )
        | RunnablePassthrough.assign(
            history=RunnableLambda(lambda x: summarize_history(x))
        )
        | prompt_template
        | llm
        | RunnableLambda(partial(check_and_search, retriever=retriever, mp_name=mp_name, mp_constituency=mp_constituency, date=date_today))
        | RunnableLambda(safely_add_message)
    )

    result = combined_chain.invoke({"question": question, "user_competency": user.get_competencies_plaintext(), "date": date_today})

    # This is not optimal but fastest way at current moment
    message_index = chat_history.get_last_message()["message_index"]

    return result, message_index