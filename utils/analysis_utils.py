from datetime import datetime
import textstat
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from transformers import pipeline

import utils.location_utils as location_utils
import utils.boto_utils as boto_utils

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()
conversation_table = boto_utils.dynamodb_init("conversations")


def zero_shot_classify(text, classifier_name, candidate_labels):
    # Classify specific candidate labels according to the message & specific classifier for specific context
    classifier = pipeline("zero-shot-classification", model=classifier_name, device=-1)
    result = classifier(text, candidate_labels)

    return result["scores"]


def get_ideology(messages):
    ideological_labels = ["Far-left", "Center-left", "Centrist", "Center-right", "Far-right"]
    ideological_hypotheses_labels = [f"This message expresses politically {label} values within UK politics" for label in ideological_labels]

    classifier_ideological = "facebook/bart-large-mnli"

    message_scores = [zero_shot_classify(message, classifier_name=classifier_ideological, candidate_labels=ideological_hypotheses_labels) for message in messages]

    return message_scores


def get_stance(messages):
    stance_labels = ["Supportive", "Neutral", "Oppositional"]
    classifier_stance = "facebook/bart-large-mnli"
    stance_hypotheses_labels = [f"This message expresses a {label} stance" for label in stance_labels]

    message_scores = [zero_shot_classify(message, classifier_name=classifier_stance, candidate_labels=stance_hypotheses_labels) for message in messages]

    return message_scores


def get_sentiment(messages):
    sentiment_labels = ["Positivity", "Neutrality", "Negativity"]
    classifier_sentiment = "facebook/bart-large-mnli"
    sentiment_hypotheses_labels = [f"This message expresses {label}" for label in sentiment_labels]

    message_scores = [zero_shot_classify(message, classifier_name=classifier_sentiment, candidate_labels=sentiment_hypotheses_labels) for message in messages]
    
    return message_scores


def get_complexity(messages):
    return [textstat.flesch_reading_ease(message) for message in messages]


def anonymize_text(text, mp_name):
    results = analyzer.analyze(text=text, entities=[], language="en")

    omit_types = ["DATE_TIME", "NRP", "LOCATION", "URL"]

    filtered_results = []
    for result in results:
        if result.entity_type in omit_types:
            continue

        matched_text = text[result.start:result.end]
        if result.entity_type == "PERSON" and matched_text in [mp_name, f"{mp_name}'s", f"{mp_name}s", f"{mp_name} MP", f"MP {mp_name}"]:
            continue

        filtered_results.append(result)
    
    anonymized = anonymizer.anonymize(text=text, analyzer_results=filtered_results)
    return anonymized.text


def analyse_chat(session_state):
    user_messages = session_state.chat_history.get_author_messages("Human")

    # Skip if no messages
    if not user_messages:
        return None
    
    mp_name = session_state.current_mp

    # 1. Anonymise
    user_messages_anonymised = [anonymize_text(message.content, mp_name) for message in user_messages]

    ai_messages = session_state.chat_history.get_author_messages("Assistant")
    ai_messages_anonymised = [anonymize_text(message.content, mp_name) for message in ai_messages]


    # 2. Analyse
    user_ward, _, user_constituency, user_ward_code, user_constituency_code = location_utils.get_location_details(session_state["location"]["coords"]["longitude"], session_state["location"]["coords"]["latitude"])

    websearch_messages_anonymised = [message for message in ai_messages_anonymised if "WEB SEARCH:" in message]
    sensitive_messages_anonymised = [message for message in ai_messages_anonymised if "SENSITIVE REPLY: " in message]
    
    chat_info = {
        # Partition key
        "mp_name": mp_name,

        # plus a extra sort-key for unique Primary Key (partition + sort key)
        "conversation_datetime": str(datetime.now()),


        "Session Date": str(session_state.session_start.date()),
        "Session Start Time": session_state.session_start.strftime("%H:%M:%S"),
        "Session Length": str(datetime.now() - session_state.session_start),

        # User Location - MAY NOT BE THE SAME AS MP
        "Ward": user_ward,
        "Ward Code": user_ward_code,
        "Constituency": user_constituency,
        "Constituency Code": user_constituency_code,

        # Have to store these as topic modelling cannot be done per-message-set on-the-fly.
        "User Messages": user_messages_anonymised,
        "Number of User Messages": len(user_messages_anonymised),
        "User Message Lengths": [len(message) for message in user_messages_anonymised],

        "Number of AI Messages": len(ai_messages_anonymised),
        "AI FRE Scores": get_complexity(ai_messages_anonymised),

        "AI Websearch Messages": websearch_messages_anonymised,
        "Number of AI Websearches": len(websearch_messages_anonymised),
        "Number of Sensitive Messages": len(sensitive_messages_anonymised),

        "User FRE Scores": get_complexity(user_messages_anonymised),
        "User Sentiment Scores": get_sentiment(user_messages_anonymised),
        "User Stance Scores": get_stance(user_messages_anonymised),
        "User Ideology Scores": get_ideology(user_messages_anonymised),

        "User Competency Scores": {name: session_state.user.get_numerical_score(value) for name, value in session_state.user.competencies.items()},

    }

    # Convert all inputs to str temporarily as DynamoDB will not accept floats. In Lambda will pull in and re-characterise var types manually
    chat_info_str = {key: str(value) for key, value in chat_info.items()}

    # 3. Send back for saving to db
    boto_utils.dynamodb_upload_record(conversation_table, chat_info_str)