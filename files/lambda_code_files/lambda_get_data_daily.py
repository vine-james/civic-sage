
import requests
import time
import json
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import os
import hashlib
import boto_utils

load_dotenv()

client_openai = OpenAI(api_key=os.getenv("OPENAI"))
index_name = "mp-data"

# Connect to the Pinecone index
pc = Pinecone(api_key=os.getenv("PINECONE"))

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

dense_index = pc.Index(index_name)


def get_embedding(text):
    response = client_openai.embeddings.create(
        model="text-embedding-ada-002",
        input=text,
    )

    return response.data[0].embedding, response.usage.total_tokens


def split_text(text, max_length=1000):
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        if len(" ".join(current_chunk + [word])) > max_length:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
        else:
            current_chunk.append(word)

    if current_chunk:
        chunks.append(" ".join(current_chunk))


    return chunks


def split_long_strings(obj, max_length=1000):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, str) and len(value) > max_length:
                obj[key] = split_text(value, max_length)

            else:
                split_long_strings(value, max_length)

    elif isinstance(obj, list):
        for item in obj:
            split_long_strings(item, max_length)

    return obj


def clean_value_types(data):
    if isinstance(data, dict):
        return {key: clean_value_types(value) for key, value in data.items()}
    
    elif isinstance(data, list):
        return [clean_value_types(item) for item in data]
    
    elif isinstance(data, bool):
        return "Yes" if data else "No"
    
    elif data is None:
        return ""
    
    elif isinstance(data, int) or isinstance(data, float):
        return str(data)
    
    else:
        return data


def batch_upsert_data(records, mp_name):
    batches = []
    batch_size = 100
    
    # Create batches of batch_size records
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        batches.append(batch)

    for current_batch in batches:
        dense_index.upsert(current_batch, namespace=mp_name)


def safe_get_nested(top_dict, nested_dict_key, default_value=None):
    if top_dict is not None and isinstance(top_dict, dict):
        return top_dict.get(nested_dict_key)
    
    return default_value


# Collected from the /Edms/ endpoint and subsequent https://oralquestionsandmotions-api.parliament.uk/EarlyDayMotion/{id}'s
def store_early_day_motions_sponsored(_, data):

    mp_early_day_motions = {}

    for edm_dict in data["items"]:
        time.sleep(0.1)
        edm_url = edm_dict["links"][0]["href"][:-5]

        mp_early_day_motions[edm_dict["value"]["title"]] = {
            "Date Motion Tabled": edm_dict["value"]["dateTabled"],
            "Number of Sponsors": edm_dict["value"]["sponsorsCount"],
        }

        response = requests.get(edm_url)
        if response.status_code == 200:
            edm_url_data = response.json()

            mp_early_day_motions[edm_dict["value"]["title"]]["Motion Text"] = edm_url_data["Response"]["MotionText"]
            mp_early_day_motions[edm_dict["value"]["title"]]["Primary Sponsor"] = edm_url_data["Response"]["PrimarySponsor"]["Name"]
            mp_early_day_motions[edm_dict["value"]["title"]]["Primary Sponsor Party"] = edm_url_data["Response"]["PrimarySponsor"]["Party"]

            mp_early_day_motions[edm_dict["value"]["title"]]["All Sponsors"] = {sponsor["Member"]["Name"] for sponsor in edm_url_data["Response"]["Sponsors"]}

        else:
            print(f"{edm_url}\nError: {response.status_code}\n\n---------------")


    return mp_early_day_motions


# Collected from the /ContributionSummary/ endpoint and subsequent https://hansard-api.parliament.uk/Debates/Debate/{id}'s
def store_contribution_summary(member_id, data):

    mp_contributions = {}

    for contributions_dict in data["items"]:
        time.sleep(0.1)
        contribution_url = contributions_dict["links"][0]["href"]

        mp_contributions[contributions_dict["value"]["debateTitle"]] = {
            "Total Contributions To Debate": contributions_dict["value"]["totalContributions"],
            "Number of Speeches": contributions_dict["value"]["speechCount"],
            "Number of Questions": contributions_dict["value"]["questionCount"],
            "Number of Supplementary Questions": contributions_dict["value"]["supplementaryQuestionCount"],
            "Number of Interventions": contributions_dict["value"]["interventionCount"],
            "Number of Answers": contributions_dict["value"]["answerCount"],
            "Number of Points of Order": contributions_dict["value"]["pointsOfOrderCount"],
            "Number of Statements": contributions_dict["value"]["statementsCount"],
            "Debate Section": contributions_dict["value"]["section"],
            "Date of Debate": contributions_dict["value"]["sittingDate"],
            "Contributions": {},
        }

        response = requests.get(contribution_url)
        if response.status_code == 200:
            contribution_url_data = response.json()

            for index, contribution in enumerate(contribution_url_data["Items"]):
                contribution_counter = 1

                if contribution["MemberId"] == member_id:
                    contribution_path = mp_contributions[contributions_dict["value"]["debateTitle"]]["Contributions"][contribution_counter] = {}
                    contribution_path["Contribution Text"] = contribution["Value"]
                    contribution_path["Timecode"] = contribution["Timecode"]

                    contribution_path["Hansard Section"] = contribution["HansardSection"]

                    # Document possible answer (the next response) -- IF it exists
                    if index + 1 < len(contribution_url_data["Items"]):
                        potential_response = contribution_url_data["Items"][index + 1]

                        contribution_path["Potential Response to Contribution"] = {
                            "Potential Respondent": potential_response["AttributedTo"],
                            "Potential Response Text": potential_response["Value"],
                            "Potential Response Timecode": potential_response["Timecode"],
                            "Potential Response Hansard Section": potential_response["HansardSection"],
                        }

                    contribution_counter += 1

        else:
            print(f"{contribution_url}\nError: {response.status_code}\n\n---------------")

    return mp_contributions


# Collected from the /Votes/ endpoint and subsequent 
def store_votes_data(_, data):
    mp_votes = {}
    # mp_votes["Total Votes Cast"] = data["totalResults"]

    for vote in data["items"]:
        mp_votes[vote["value"]["title"]] = {
            "Date of Vote": vote["value"]["date"],

            "Division Number": vote["value"]["divisionNumber"],

            "Voted Aye": vote["value"]["inAffirmativeLobby"],
            "Acted as a Teller of the Vote": vote["value"]["actedAsTeller"],

            "Total Votes In Favour (Aye)": vote["value"]["numberInFavour"],
            "Total Votes Against (No)": vote["value"]["numberAgainst"],
        }

    return mp_votes


# Collected from the /WrittenQuestions/ endpoint and subsequent 
def store_written_questions_data(_, data):
    mp_written_questions = {}

    # mp_written_questions["Total Written Questions"] = data["totalResults"]
    
    for question_dict in data["items"]:

        # Using .get() here as have noticed some archived records have None fields dispersed randomly.
        mp_written_questions[question_dict["value"]["heading"]] = {
            "Question to Organisation": question_dict["value"]["answeringBody"].get("name", "Unknown Organisation"),
            "Question to Organisation Representative Title": question_dict["value"]["answeringBody"].get("target", "Unknown Title"),
            "Question to Organisation Representative Name": safe_get_nested(question_dict["value"]["answeringMember"], "nameDisplayAs", "Unknown Name"),
            "Question to Organisation Representative Party": safe_get_nested(question_dict["value"]["answeringMember"], "latestParty", "Unknown Party"),
            
            "Date Question Submitted": question_dict["value"].get("dateTabled", "Unknown Date"),
            "Date Scheduled For Answer": question_dict["value"].get("dateForAnswer", "Unknown Date"),
            "Date Question Answered": question_dict["value"].get("dateAnswered", "Unknown Date"),

            "Question": question_dict["value"].get("questionText", "No Question Provided"),
            "Answer": question_dict["value"].get("answerText", "No Answer Provided"),

            "Is Question Withdrawn": question_dict["value"].get("isWithdrawn", False),
            "Is Answer Holding": question_dict["value"].get("answerIsHolding", False),
            "Is Answer Correction": question_dict["value"].get("answerIsCorrection", False),
            "Is Named Day": question_dict["value"].get("isNamedDay", False),
            "Does Member Have Interest": question_dict["value"].get("memberHasInterest", False),
        }
    
    return mp_written_questions


parliament_api = {
    "Members": {
        "base_url": "https://members-api.parliament.uk/api/Members/",
        "apis": {
            "Supported Early Day Motions": {"path": "{id}/Edms?", "function": store_early_day_motions_sponsored, "pagination": True, "source": "https://members.parliament.uk/member/{id}/earlydaymotions", "latest_record_field": "id"},
            "Spoken Contributions": {"path": "{id}/ContributionSummary?", "function": store_contribution_summary, "pagination": True, "source": "https://members.parliament.uk/member/{id}/contributions", "latest_record_field": "debateId"},
            "Voting": {"path": "{id}/Voting?house=1&", "function": store_votes_data, "pagination": True, "source": "https://members.parliament.uk/member/{id}/voting", "latest_record_field": "id"},
            "Submitted Written Questions": {"path": "{id}/WrittenQuestions?", "function": store_written_questions_data, "pagination": True, "source": "https://members.parliament.uk/member/{id}/writtenquestions", "latest_record_field": "uin"},
        },
    },
}


def transform_to_text(data):
    result = []
    
    if not isinstance(data, str):
        for section, content in data.items():

            if isinstance(content, dict):
                section_text = f"{section}:\n"

                for key, value in content.items():
                    if isinstance(value, dict):
                        section_text += f"  {key}:\n"
                        for sub_key, sub_value in value.items():
                            section_text += f"    {sub_key}: {sub_value}\n"

                    else:
                        section_text += f"  {key}: {value}\n"
            else:
                section_text = f"{section}: {content}\n"
            
            result.append(section_text)
        
        return "\n".join(result)
    
    else:
        return data


def prepare_data_for_upsert(metadata, source, batch_records):
    text_data = transform_to_text(metadata)
    id = hashlib.md5(text_data.encode()).hexdigest()

    embedding, tokens_used = get_embedding(text_data)

    print(f"Batching for upsert: {text_data}")
    
    batch_records.append((id, embedding, {"text": text_data, "data_source": source}))

    return batch_records


def save_raw_data_db(mp_name, mp_id, mp_data):
    # Extract only whats needed, into a summary dictionary

    mp_summary = {
        # mp_name is the partition key for AWS Table
        "mp_name": mp_data["Parliament"]["General Details"]["Full Name"],
        "Picture": f"https://members-api.parliament.uk/api/Members/{mp_id}/Portrait",
        "Party": mp_data["Parliament"]["General Details"]["Current Party"],
        "Constituency": mp_data["Parliament"]["General Details"]["Current Constituency"],
        "Email": mp_data["Parliament"]["Contact Details"]["email"],
    }

    # Add these conditional ones if they exist
    optional_social_media = ["Website", "Facebook", "X (formerly Twitter)"]

    for social_media in optional_social_media:
        if social_media in mp_data["Parliament"]["Contact Details"]:
            mp_summary[social_media] = mp_data["Parliament"]["Contact Details"][social_media]["url"]

    # More complex behaviour
    # Elections
    mp_summary["Elections"] = []

    for constituency, election_dict in mp_data["Parliament"]["Biography"]["Constituencies Elected"].items():
        mp_summary["Elections"].append({"Constituency": constituency, "Date": election_dict["Start"], "Result": "Won election"})

    for constituency, election_dict in mp_data["Parliament"]["Biography"]["Elections Contested"].items():
        mp_summary["Elections"].append({"Constituency": constituency, "Date": election_dict["Date"], "Result": "Lost election"})

    # Posts
    mp_summary["Government Posts Held"] = []
    for post, post_dict in mp_data["Parliament"]["Biography"]["Government Posts Held"].items():
        mp_summary["Government Posts Held"].append({"Post": post, "Start": post_dict["Start"], "End": post_dict["End"], "Department": post_dict["Info"]})

    mp_summary["Opposition Posts Held"] = []
    for post, post_dict in mp_data["Parliament"]["Biography"]["Opposition Posts Held"].items():
        mp_summary["Opposition Posts Held"].append({"Post": post, "Start": post_dict["Start"], "End": post_dict["End"], "Department": post_dict["Info"]})

    mp_summary["Committee Memberships Held"] = []
    for post, post_dict in mp_data["Parliament"]["Biography"]["Committee Memberships Held"].items():
        mp_summary["Committee Memberships Held"].append({"Post": post, "Start": post_dict["Start"], "End": post_dict["End"]})


    # Save to db
    boto_table = boto_utils.dynamodb_init("summaries")
    boto_utils.dynamodb_upload_record(data=mp_summary, table=boto_table)


def store_mp_data(mp_name, mp_id, mp_data):

    # Store MP data in it's python form to Amazon DynamoDB
    # save_raw_data_db(mp_name, mp_id, mp_data)
    
    # Change every entry of bool 'false' / 'true' to str "No" / "Yes"
    mp_json_bool_cleaned_data = clean_value_types(mp_data)
    mp_chunked_json_data = split_long_strings(mp_json_bool_cleaned_data, max_length=1000)

    data_processing_types = {
        "Group": ["Biography", "Synopsis", "General Details", "Contact Details", "Latest Election Details", "Registered Interests"],
        "Separate": ["Spoken Contributions", "Submitted Written Questions", "Supported Early Day Motions", "Voting"],
    }


    records = []
    for data_section, api_data_dict in parliament_api["Members"]["apis"].items():
        if data_section in data_processing_types["Separate"]:

            if data_section in mp_chunked_json_data["Parliament"]:
                metadata = mp_chunked_json_data["Parliament"][data_section]
                # metadata_summary = {"subject": f"Summary of {data_section} topics"}
                # metadata_summary[f"Summary of {data_section} topics"] = []

                # for key, value in metadata.items():
                #     if not isinstance(value, dict):
                #         metadata_summary[key] = value

                #     else:
                #         metadata_summary[f"Summary of {data_section} topics"].append(key)

                # Individual
                for key, value in metadata.items():
                    if isinstance(value, dict):
                        metadata_individual_record = {key: value, "subject": f"Individual record of {data_section} ({key})"}
                        records = prepare_data_for_upsert(metadata_individual_record, api_data_dict["source"].replace("{id}", str(mp_id)), records)

        elif data_section in data_processing_types["Group"]:
            metadata = mp_chunked_json_data["Parliament"][data_section]
            
            records = prepare_data_for_upsert(metadata, api_data_dict["source"].replace("{id}", str(mp_id)), records)


    batch_upsert_data(records, mp_name)


def send_api_request(url):
    response = requests.get(url)
   
    if response.status_code == 200:
        data = response.json()
        return data
    
    else:
        print(f"{url}\nError: {response.status_code}\n\n---------------")
        return None


mp_daily_update_table = boto_utils.dynamodb_init("mp-daily-update-records")


# Manually get the member IDs
mp_list = [
    {"Name": "Paul Holmes", "ID": 4803}, # Hamble Valley MP
    {"Name": "Jessica Toale", "ID": 5202}, # Bournemouth West MP
    {"Name": "Tom Hayes", "ID": 5210}, # Bournemouth East MP
]

def collect_mp_data(mps_to_query):
    for member_dict in mps_to_query:

        # Structure of naming conventions for the dictionary is somewhat intentionally strange due to way it will eventually be converted to JSON and then flattened
        # Query all of the APIs for the 'member' type and store according to functions

        mp_data = {}
        mp_data_source_parliament = {}

        api_type = "Members"

        mp_new_latest_records_dict = {
            "mp_name": member_dict["Name"],
        }
        mp_latest_records = boto_utils.dynamodb_fetch_record(mp_daily_update_table, "mp_name", member_dict["Name"])


        for name, api_dict in parliament_api[api_type]["apis"].items():
            append_id_url = api_dict["path"].replace("{id}", str(member_dict["ID"]))
            api_url = f"{parliament_api[api_type]['base_url']}{append_id_url}"

            data = None

            if api_dict["pagination"]:
                counter = 1
                # Do first page separately
                page_data = send_api_request(f"{api_url}page={counter}")
                first_page_entry = page_data

                database_latest_record_identifier = int(mp_latest_records[api_dict["path"]]) if mp_latest_records[api_dict["path"]] != "None" else mp_latest_records[api_dict["path"]]

                if page_data["items"]:
                    # First checking if any records exist
                    search_latest_record_identifier = int(page_data["items"][0]["value"][api_dict["latest_record_field"]])
                    mp_new_latest_records_dict[api_dict["path"]] = search_latest_record_identifier
                else:
                    mp_new_latest_records_dict[api_dict["path"]] = "None"

                
                # Check first entry of first page is not already recorded
                if (database_latest_record_identifier == search_latest_record_identifier):
                    print(f"[{member_dict["Name"]}]: Found latest record as first entry in first page {api_dict["path"]} -- {database_latest_record_identifier} == {search_latest_record_identifier}")
                    continue

                skip_current_loop = False

                first_page_entry = {"items": []}

                # Now check every entry in first page is not already recorded, append records for upload until its found
                for i, item in enumerate(page_data["items"]):
                    time.sleep(1)
                    if (database_latest_record_identifier == int(item["value"][api_dict["latest_record_field"]])):
                        print(f"[{member_dict["Name"]}]: Found latest record in first page, ({i}) {api_dict["path"]} -- {database_latest_record_identifier} == {int(item["value"][api_dict["latest_record_field"]])}")
                        skip_current_loop = True
                        break
                    
                    first_page_entry["items"].append(item)
                
                # Need to add this flag so that if we found a record in the first page, skip the current loop and move onto next API rather than now storing every record for additional pages
                if skip_current_loop:
                    data = first_page_entry
                    mp_data_source_parliament[name] = api_dict["function"](member_dict["ID"], data)
                    # breakpoint()
                    continue

                # Now iteratively check every record in every other page, append records for upload until its found
                # print(f"Not the same {api_dict["path"]} -- {database_latest_record_identifier} == {search_latest_record_identifier}")
                while page_data["items"]:
                    counter +=1
                    page_data = send_api_request(f"{api_url}page={counter}")
                    print(f"[{member_dict["Name"]}]: Requesting {api_url}page={counter}")
                    
                    for i, item in enumerate(page_data["items"]):
                        if (database_latest_record_identifier == int(item["value"][api_dict["latest_record_field"]])):
                            print(f"[{member_dict["Name"]}]: Found latest record in page {counter}, ({i}) {api_dict["path"]} -- {database_latest_record_identifier} == {search_latest_record_identifier}")
                            continue
                        
                        first_page_entry["items"].append(item)

                    time.sleep(0.1)
                
                data = first_page_entry
            else:
                data = send_api_request(api_url)

            mp_data_source_parliament[name] = api_dict["function"](member_dict["ID"], data)
            time.sleep(0.1)


        if mp_data_source_parliament:
            print(f"[{member_dict["Name"]}]: New data found, proceeding to store. {mp_data_source_parliament}")
                
            boto_utils.dynamodb_upload_record(data=mp_new_latest_records_dict, table=mp_daily_update_table)
            
            mp_data["Parliament"] = mp_data_source_parliament
            store_mp_data(member_dict["Name"], member_dict["ID"], mp_data)

        else:
            print(f"[{member_dict["Name"]}]: No new data found, ending!")



collect_mp_data(mp_list)