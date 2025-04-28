


import utils.rag_llm_utils as rag_llm_utils




# prompt_template = """
# You are an Assistant designed to evaluate the response of AI systems.

# You have been given a key fact, labelled below.
# You have also been given an initial question which is designed to assess whether the AI system can provide an answer referencing your provided key fact.
# You have also been given the AI systems response to the initial question.

# Your job is to assess whether the provided response satisfactorily provides the information detailed in the key fact.

# If the answer is satisfactory, reply with the exact statement "SATISFACTORY" and nothing else.
# If the answer is not satisfactory, rephrase the original question to be more specific to encourage the AI system to provide the key fact you are looking for.
# """



"""
You are an Assistant whose job is to check if an AI’s answer includes a specific key fact.

Here’s what you will get:

- A key fact that should be included in the answer.
- A question that the AI was asked.
- The AI’s response to the question.

Your task:
- If the AI’s answer includes the key fact, respond with just: "SATISFACTORY"
- If the AI’s answer does NOT include the key fact, rewrite the original question so it is more clear and direct, guiding the AI system to include the key fact next time.
"""


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


eval_prompt_template = ChatPromptTemplate.from_messages(
    [
        SystemMessage(
            content="""
            You are an Assistant whose job is to check if an AI’s answer includes a specific key fact.

            Here’s what you will get:

            - A key fact that should be included in the answer.
            - A question that the AI was asked.
            - The AI’s response to the question.

            Your task:
            - If the AI’s answer includes the key fact, respond with just: "SATISFACTORY"
            - If the AI’s answer does NOT include the key fact, rewrite the original question based on the additional information learned through the AI's response so it is closer to eliciting the key fact.
            """
        ),
        ("human", "Key fact: {key_fact}"),
        ("human", "Question asked to AI: {original_question}"),
        ("human", "AI's response to question: {ai_response}"),
    ]
)

# def classify_output(result):
#     # Classify output as either satisfactory or unsatisfactory

#     if hasattr(result, "content"):
#         # If results are too personal, re-direct.
#         if result.content.strip() == "SATISFACTORY":
#             print("Satisfactory")

#         else:
#             print("Unsatisfactory: ", result)


#     breakpoint()


llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=constants.TOKEN_OPENAI,
)

evaluation_chain = eval_prompt_template | llm
# evaluation_chain = eval_prompt_template | llm | RunnableLambda(classify_output)




def evaluate_output(key_fact, current_question_version, current_response_version):
    return evaluation_chain.invoke({
        "key_fact": key_fact, 
        "original_question": current_question_version,
        "ai_response": current_response_version,
    })



# def run_evaluation_cycle(key_fact, question):
#     # Run it once separately then begin chain

#     response = llmchainhere() - classify_output()

#     # This is messed up, need to work this out.

#     if response satisfactory:
#         do something
#     else
#         evaluate_output(response)
    

#     evaluation_output = evaluation_chain.invoke({
#         "key_fact": key_fact, 
#         "original_question": question,
#         "ai_response": 1,
#     })

"""

A vote where he voted yes
A vote where he voted no


How many written questions? (This will change over time)

"""

from collections import namedtuple

TestSuite_MP = namedtuple("TestSuite_MP", ["name", "constituency", "tests"])
TestCase = namedtuple("TestCase", ["subject", "fact", "q"])

TESTS = [
    TestSuite_MP(
        name="Paul Holmes",
        constituency="Hamble Valley",
        tests=[
            # TestCase(
            #     subject="Elections",
            #     fact="""
            #         Paul Holmes has won elections in:
            #         - Hamble Valley on 04/07/2024
            #         - Eastleigh on 12/12/2019
            #     """,
            #     q="Where and when have they won an election?",
            # ),
            # TestCase(
            #     subject="Current Political Party",
            #     fact="""
            #         Paul Holmes is currently part of the Conservative Party.
            #     """,
            #     q="What party do they belong to?",
            # ),
            # TestCase(
            #     subject="Opposition Roles",
            #     fact="""
            #         Paul Holmes has held the following roles as part of the Opposition:
            #         - Shadow Parliamentary Under Secretary in the Ministry of Housing, Communities and Local Government (08/11/2024 - Current)
            #         - Shadow Minister in the Foreign, Commonwealth and Development Office (19/07/2024 - 06/11/2024)
            #         - Shadow Minister in the Northern Ireland Office (19/07/2024 - 06/11/2024)
            #         - Opposition Whip in the Whips Office (19/07/2024 - Current)
            #     """,
            #     q="What are their opposition roles?",
            # ),
            # TestCase(
            #     subject="Latest Election Details",
            #     fact="""
            #         Paul Holmes (Conservatives) came 1st in the election, achieving 19,671 votes (36.4% share)
            #         Prad Bains (Liberal Democrats) came 2nd in the election, achieving 14,869 votes (27.5% share)
            #     """,
            #     q="What was their latest election statistics and who came 2nd?",
            # ),
            TestCase(
                subject="Recent Vote",
                fact="""
                    Paul Holmes voted 'No' on the Tobacco and Vapes Bill: Third Reading on the 26th March 2025. There were 366 'Ayes' and '41' Noes.
                """,
                q="What did they vote for on Tobacco and Vapes legislation?",
            ),
            TestCase(
                subject="Registered Interests",
                fact="""
                    Paul Holmes registered interests include:
                    - Commissioner of the Key Worker Homes Fund, paid £0.
                    - Trustee of the Armed Forces Parliamentary Scheme, paid £0.
                    - A payment from Valary Management Limited, paid £2,500.
                """,
                q="What are all of their registered interests, and how much were they paid?",
            ),
        ]
    ),
]


# Pre-setup
MPS = [
    {"Name": "Paul Holmes", "Constituency": "Hamble Valley"},
    {"Name": "Jessica Toale", "Constituency": "Bournemouth West"},
    {"Name": "Tom Hayes", "Constituency": "Bournemouth East"},
]

MAX_TEST_ATTEMPTS = 3

preset_user = rag_llm_utils.User(competencies={
    "UK Politics": "Nothing at all",
    "UK Parliament": "Nothing at all",
    "UK Government": "Nothing at all",
})

logs = {mp_dict["Name"]: {} for mp_dict in MPS}


def evaluate_test_case_cycle(mp_name, mp_constituency, user, question, test_case, test_logs):
    llm_response, _ = rag_llm_utils.ask_prompt(question, user, mp_name, mp_constituency)

    test_logs["Questions"].append(question)
    test_logs["Civic Sage Responses"].append(llm_response)

    evaluated_output = evaluate_output(
        key_fact=test_case.fact,
        current_question_version=question,
        current_response_version=llm_response,
    )

    if evaluated_output.content.strip() == "SATISFACTORY":
        print(f"[{mp_name}]: {test_case.subject.upper()} passed! {len(test_logs['Questions'])} prompt turns.")
        return f"Passed ({len(test_logs['Questions'])} / {MAX_TEST_ATTEMPTS})"

    else:
        if len(test_logs["Questions"]) >= MAX_TEST_ATTEMPTS:
            print(f"[{mp_name}]: {test_case.subject.upper()} failed! Shutting down test due to exceeding max retries {len(test_logs['Questions'])} / {MAX_TEST_ATTEMPTS}")
            return "Failed"

        print(f"[{mp_name}]: {test_case.subject.upper()} failed! Current attempt: {len(test_logs['Questions'])}")
        evaluate_test_case_cycle(mp_name, mp_constituency, user, evaluated_output.content, test_case, test_logs)

for mp_test_suite in TESTS:
    print(f"----------\n[!] Running all tests for {mp_test_suite.name}")

    for test_case in mp_test_suite.tests:
        print(f"[{mp_test_suite.name}]: Running {test_case.subject.upper()} test!")

        logs_current_test = logs[mp_test_suite.name][test_case.subject] = {
            "Fact": test_case.fact,
            "Questions": [],
            "Civic Sage Responses": [],
        }

        evaluate_test_case_cycle(mp_test_suite.name, mp_test_suite.constituency, preset_user, test_case.q, test_case, logs_current_test)

print(logs)

"""

1. Query RAG LLM with initial question
2. Get RAG LLM response
3. Input RAG LLM response, iniital question and key fact into evaluate_output()
    If response good, say 'SATSIFACTORY'
    If response bad, rephrase and output REPHRASED_QUESTION.

4. If respones == 'SATISFACTORY' 
    break
    ADD QUESTION to array
    do xyz

    else:
        Add QUESTION to array
        Repeat 1-3.

4. Query RAG LLM with new response
5. Get RAG LLM response
6. Input RAG LLM response, iniital question and key fact into evaluate_output()

4. If RAG LLM response != SATISFACTORY
        Loop steps 2-3, for each fail add the rephrased question into it
ELSE
    end, summarise key facts like num of response turns. Each of the question rephrases.


"""