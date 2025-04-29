
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from collections import namedtuple

import utils.rag_llm_utils as rag_llm_utils
import utils.constants as constants

# Pre-setup
TestSuite_MP = namedtuple("TestSuite_MP", ["name", "constituency", "tests"])
TestCase = namedtuple("TestCase", ["subject", "fact", "q"])

TESTS = [
    TestSuite_MP(
        name="Paul Holmes",
        constituency="Hamble Valley",
        tests=[
            TestCase(
                subject="Elections",
                fact="""
                    Paul Holmes has won elections in:
                    - Hamble Valley on 04/07/2024
                    - Eastleigh on 12/12/2019
                """,
                q="Where and when have they won an election?",
            ),
            TestCase(
                subject="Current Political Party",
                fact="""
                    Paul Holmes is currently part of the Conservative Party.
                """,
                q="What party do they belong to?",
            ),
            TestCase(
                subject="Opposition Roles",
                fact="""
                    Paul Holmes has held the following roles as part of the Opposition:
                    - Shadow Parliamentary Under Secretary in the Ministry of Housing, Communities and Local Government (08/11/2024 - Current)
                    - Shadow Minister in the Foreign, Commonwealth and Development Office (19/07/2024 - 06/11/2024)
                    - Shadow Minister in the Northern Ireland Office (19/07/2024 - 06/11/2024)
                    - Opposition Whip in the Whips Office (19/07/2024 - Current)
                """,
                q="What are their opposition roles?",
            ),
            TestCase(
                subject="Latest Election Details",
                fact="""
                    Paul Holmes (Conservatives) came 1st in the election, achieving 19,671 votes (36.4% share)
                    Prad Bains (Liberal Democrats) came 2nd in the election, achieving 14,869 votes (27.5% share)
                """,
                q="What was their latest election statistics and who came 2nd?",
            ),
            TestCase(
                subject="Recent Vote",
                fact="""
                    Paul Holmes voted 'No' on the Tobacco and Vapes Bill: Third Reading on the 26th March 2025. There were 366 'Ayes' and 41 'Noes'.
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


    TestSuite_MP(
        name="Jessica Toale",
        constituency="Bournemouth West",
        tests=[
            TestCase(
                subject="Elections",
                fact="""
                    Jessica Toale has won elections in:
                    - Bournemouth West on 04/07/2024
                """,
                q="Where and when have they won an election?",
            ),
            TestCase(
                subject="Current Political Party",
                fact="""
                    Jessica Toale is currently part of the Labour Party.
                """,
                q="What party do they belong to?",
            ),
            TestCase(
                subject="Opposition Roles",
                fact="""
                    Jessica Toale has held the following roles as part of the Opposition:
                    - None
                """,
                q="What are their opposition roles?",
            ),
            TestCase(
                subject="Latest Election Details",
                fact="""
                    Jessica Toale (Labour) came 1st in the election, achieving 14,365 votes (36.4% share)
                    Conor Burns (Conservative) came 2nd in the election, achieving 11,141 votes (28.3% share)
                """,
                q="What was their latest election statistics and who came 2nd?",
            ),
            TestCase(
                subject="Recent Vote",
                fact="""
                    Jessica Toale voted 'Aye' on the Children's Wellbeing and Schools Bill: Third Reading on the 18th March 2025. There were 382 'Ayes' and 104 'Noes'.
                """,
                q="What did they vote for on the topic of Children's Welfare?",
            ),
            TestCase(
                subject="Registered Interests",
                fact="""
                    Jessica Toale's registered interests include:
                    - A payment from Gary Lubner, paid £15,000.
                    - A payment from Poole Bay Holdings, paid £15,000.
                    - A payment from GMB Southern Region, paid £10,000.
                    - A payment from Labour Together Limited, paid £5,000.
                    - A payment from Julia Davies, paid £5,000.
                    - A payment from Labour Friends of Israel, paid £1,950.
                    - Owning residential property in London.
                    - Renting a residential property in London.
                    - Renting another residential property in London as part of a company with other family members.
                """,
                q="What are all of their registered interests, and how much were they paid?",
            ),
        ],
    ),


    TestSuite_MP(
        name="Tom Hayes",
        constituency="Bournemouth East",
        tests=[
            TestCase(
                subject="Elections",
                fact="""
                    Tom Hayes Holmes has won elections in:
                    - Bournemouth East on 04/07/2024
                """,
                q="Where and when have they won an election?",
            ),
            TestCase(
                subject="Current Political Party",
                fact="""
                    Tom Hayes is currently part of the Labour Party.
                """,
                q="What party do they belong to?",
            ),
            TestCase(
                subject="Opposition Roles",
                fact="""
                    Paul Holmes has held the following roles as part of the Opposition:
                    - None
                """,
                q="What are their opposition roles?",
            ),
            TestCase(
                subject="Latest Election Details",
                fact="""
                    Tom Hayes (Labour) came 1st in the election, achieving 18,316 votes (40.8% share)
                    Tobias Ellwood (Conservative) came 2nd in the election, achieving 12,837 votes (28.6% share)
                """,
                q="What was their latest election statistics and who came 2nd?",
            ),
            TestCase(
                subject="Recent Vote",
                fact="""
                    Tom Hayes voted 'Aye' on the Great British Energy Bill: Third Reading on the 29 October 2024. There were 361 'Ayes' and 111 'Noes'.
                """,
                q="What did they vote for on Great British Energy?",
            ),
            TestCase(
                subject="Registered Interests",
                fact="""
                    Tom Hayes registered interests include:
                    - A payment from Gary Lubner, paid £15,000.
                    - A payment from Arden Strategies, paid estimated £2,320.85.
                    - A payment from The Communication Workers Union, paid £2,750.
                    - A payment from GMB Southern Region, paid £10,000.
                    - A payment from Labour Together Limited, paid £5,000.
                    - A role as CEO of Elmore Community Services, paid £2,423.60.
                """,
                q="What are all of their registered interests, and how much were they paid?",
            ),
        ],
    ),

]


MPS = [
    {"Name": "Paul Holmes", "Constituency": "Hamble Valley"},
    {"Name": "Jessica Toale", "Constituency": "Bournemouth West"},
    {"Name": "Tom Hayes", "Constituency": "Bournemouth East"},
]

MAX_TEST_ATTEMPTS = 3

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
            - If the AI’s answer does NOT include the key fact, respond by rephrasing the question to be related to underlying concepts that could lead to the key fact being included in a future response. DO NOT include any other message content.            
            """
        ),
        ("human", "Key fact: {key_fact}"),
        ("human", "Question asked to AI: {original_question}"),
        ("human", "AI's response to question: {ai_response}"),
    ]
)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=constants.TOKEN_OPENAI,
)

evaluation_chain = eval_prompt_template | llm


preset_user = rag_llm_utils.User(competencies={
    "UK Politics": "Nothing at all",
    "UK Parliament": "Nothing at all",
    "UK Government": "Nothing at all",
})

logs = {mp_dict["Name"]: {} for mp_dict in MPS}


def evaluate_output(key_fact, current_question_version, current_response_version):
    return evaluation_chain.invoke({
        "key_fact": key_fact, 
        "original_question": current_question_version,
        "ai_response": current_response_version,
    })


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