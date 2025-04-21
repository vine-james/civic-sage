# Lambda script for analysing chats at scale
from collections import Counter
import itertools
from calendar import monthrange
import boto_utils
import pandas as pd
import ast
from io import StringIO
import numpy as np
import yake
from datetime import datetime

CONSTITUENCY_WARDS = {
    "Hamble Valley": {
        "Ward Name": [
            "Botley",
            "Bursledon and Hound North",
            "Hamble and Netley",
            "Hedge End North",
            "Hedge End South",
            "Avenue",
            "Hook-with-Warsash",
            "Locks Heath",
            "Park Gate",
            "Sarisbury and Whiteley",
            "Stubbington",
            "Titchfield",
            "Titchfield Common",
            "Whiteley and Shedfield",
        ],

        "Ward Code": [
            "E05011188",
            "E05011189",
            "E05011195",
            "E05011196",
            "E05011197",
            "E05015664",
            "E05015669",
            "E05015670",
            "E05015671",
            "E05015674",
            "E05015675",
            "E05015676",
            "E05015677",
            "E05011009",
        ],
    },

    "Bournemouth East": {
        "Ward Name": [
            "Boscombe East and Pokesdown",
            "Boscombe West",
            "East Cliff and Springbourne",
            "East Southbourne and Tuckton",
            "Littledown and Iford",
            "Moordown",
            "Muscliff and Strouden Park",
            "Queen's Park",
            "West Southbourne",
        ],

        "Ward Code": [
            "E05012651",
            "E05012652",
            "E05012661",
            "E05012662",
            "E05012666",
            "E05012667",
            "E05012669",
            "E05012675",
            "E05012679",
        ],
    },


    "Bournemouth West": {
        "Ward Name": [
            "Alderney and Bourne Valley",
            "Bournemouth Central",
            "Kinson",
            "Redhill and Northbourne",
            "Talbot and Branksome Woods",
            "Wallisdown and Winton West",
            "Westbourne and West Cliff",
            "Winton East",
        ],

        "Ward Code": [
            "E05012649",
            "E05012653",
            "E05012665",
            "E05012676",
            "E05012677",
            "E05012678",
            "E05012680",
            "E05012681",
        ],   
        
    },
}


MPS = [
    {"Name": "Paul Holmes", "Constituency": "Hamble Valley"},
    {"Name": "Jessica Toale", "Constituency": "Bournemouth West"},
    {"Name": "Tom Hayes", "Constituency": "Bournemouth East"},
]

conversation_table = boto_utils.dynamodb_init("conversations")
reported_responses_table = boto_utils.dynamodb_init("message-reports")


def save_df_to_s3(df_chart, mp_name, chart_name):
    # Save a DF, formatted for a specific chart, as a .csv to the S3 bucket
    csv_buffer = StringIO()
    df_chart.to_csv(csv_buffer, index=False)

    boto_utils.s3_upload(csv_buffer.getvalue().encode("utf-8"), f"{mp_name}/{chart_name}.csv")


def _num_by_day(df_to_use, current_year, current_month, date_col, num_col):
    num_days = monthrange(current_year, current_month)[1]
    all_days = pd.date_range(
        start=f"{current_year}-{current_month:02d}-01",
        periods=num_days
    ).date

    df_num_by_day = pd.DataFrame({date_col: all_days})

    count_by_day = df_to_use.groupby(date_col).size().reset_index(name=num_col)

    df_num_by_day[date_col] = pd.to_datetime(df_num_by_day[date_col])
    count_by_day[date_col] = pd.to_datetime(count_by_day[date_col])
    df_num_by_day = df_num_by_day.merge(count_by_day, on=date_col, how="left").fillna(0)
    df_num_by_day[num_col] = df_num_by_day[num_col].astype(int)
    df_num_by_day[date_col] = df_num_by_day[date_col].dt.date

    return df_num_by_day


def make_df_chart_sessions_by_day_line(df, mp_name, constituency):
    df_constituency = df[df["Constituency"] == constituency]
    df_non_constituency = df[df["Constituency"] != constituency]
    
    current_month = datetime.now().month
    current_year = datetime.now().year

    df_inside = _num_by_day(df_constituency, current_year, current_month, "Session Date", "Sessions")
    df_outside = _num_by_day(df_non_constituency, current_year, current_month, "Session Date", "Sessions")

    df_inside["Constituency"] = "Inside"
    df_outside["Constituency"] = "Outside"

    df_combined = pd.concat([df_inside, df_outside], ignore_index=True)

    save_df_to_s3(df_combined, mp_name, "month_sessions_by_day")


def make_df_chart_sessions_by_ward_map(df, mp_name, constituency):
    df_constituency = df[df["Constituency"] == constituency]

    wards = CONSTITUENCY_WARDS[constituency]

    df_sessions_by_ward = pd.DataFrame({
        "Ward": wards["Ward Name"],
        "Ward Code": wards["Ward Code"],
    })

    df_sessions_by_ward["Sessions"] = df_sessions_by_ward["Ward"].map(df_constituency["Ward"].value_counts()).fillna(0).astype(int)

    outside_row =  pd.DataFrame({"Ward": ["Outside"], "Ward Code": "NONE", "Sessions": [len(df[df["Constituency"] != constituency])]})

    df_sessions_by_ward = pd.concat([df_sessions_by_ward, outside_row], ignore_index=False).reset_index(drop=True)


    save_df_to_s3(df_sessions_by_ward, mp_name, "month_sessions_by_ward")


def make_df_chart_political_knowledge_by_ward_map(df, mp_name, constituency):
    df_constituency = df[df["Constituency"] == constituency]

    df_non_constituency = df[df["Constituency"] != constituency]

    wards = CONSTITUENCY_WARDS[constituency]

    df_competencies_by_ward = df_constituency.groupby("Ward")[["UK Politics", "UK Government", "UK Parliament"]].mean().reset_index().round(0)

    df_competencies_outside = df_non_constituency[["UK Politics", "UK Government", "UK Parliament"]].mean()
    df_competencies_outside = df_competencies_outside.fillna(0).round(0)
    
    df_other_data = pd.DataFrame({
        "Ward": wards["Ward Name"],
        "Ward Code": wards["Ward Code"],
    })

    df_competencies_by_ward = df_other_data.merge(df_competencies_by_ward, on="Ward", how="left").fillna(0)

    outside_row = df_competencies_outside.to_frame().T
    outside_row["Ward"] = "Outside"
    outside_row["Ward Code"] = "NONE"

    df_competencies_by_ward = pd.concat([df_competencies_by_ward, outside_row], ignore_index=True)
    
    save_df_to_s3(df_competencies_by_ward, mp_name, "month_political_knowledge_by_ward")


def make_df_chart_conversations_by_hour_bar(df, mp_name, constituency):
    df_constituency = df[df["Constituency"] == constituency]
    df_non_constituency = df[df["Constituency"] != constituency]

    df_constituency["Hour"] = df_constituency["Session Start Time"].dt.total_seconds() // 3600
    df_non_constituency["Hour"] = df_non_constituency["Session Start Time"].dt.total_seconds() // 3600

    bins = [0, 4, 8, 12, 16, 24] 
    labels = ["00:00-03:59", "04:00-07:59", "08:00-11:59", "12:00-15:59", "16:00-23:59"]

    df_constituency["Time Bins"] = pd.cut(df_constituency["Hour"], bins=bins, labels=labels, right=False, include_lowest=True)
    df_non_constituency["Time Bins"] = pd.cut(df_non_constituency["Hour"], bins=bins, labels=labels, right=False, include_lowest=True)

    constituency_counts = df_constituency["Time Bins"].value_counts().sort_index()
    df_constituency_results = constituency_counts.reset_index()
    df_constituency_results.columns = ["Time Period", "Count"]
    df_constituency_results["Constituency"] = ["Inside"] * len(df_constituency_results)

    non_constituency_counts = df_non_constituency["Time Bins"].value_counts().sort_index()
    df_non_constituency_results = non_constituency_counts.reset_index()
    df_non_constituency_results.columns = ["Time Period", "Count"]
    df_non_constituency_results["Constituency"] = ["Outside"] * len(df_non_constituency_results)

    df_outcome = pd.concat([df_constituency_results, df_non_constituency_results], ignore_index=True)

    save_df_to_s3(df_outcome, mp_name, "month_conversations_by_hour")


def make_df_chart_conversations_by_length_bar(df, mp_name, constituency):
    df_constituency = df[df["Constituency"] == constituency]
    df_non_constituency = df[df["Constituency"] != constituency]

    df_constituency["Session Length Seconds"] = df_constituency["Session Length"].dt.total_seconds()
    df_non_constituency["Session Length Seconds"] = df_non_constituency["Session Length"].dt.total_seconds()

    bins = [0, 60, 300, 900, 1800, 3600, float("inf")]
    labels = [
        "Less than 1 minute",
        "1-5 minutes",
        "5-15 minutes",
        "15-30 minutes",
        "30 minutes to 1 hour",
        "1 hour+"
    ]

    df_constituency["Session Length Bins"] = pd.cut(
    df_constituency["Session Length Seconds"], bins=bins, labels=labels, right=False, include_lowest=True)
    df_non_constituency["Session Length Bins"] = pd.cut(
    df_non_constituency["Session Length Seconds"], bins=bins, labels=labels, right=False, include_lowest=True)

    constituency_counts = df_constituency["Session Length Bins"].value_counts().sort_index()
    df_constituency_results = constituency_counts.reset_index()
    df_constituency_results.columns = ["Session Length", "Count"]
    df_constituency_results["Constituency"] = ["Inside"] * len(df_constituency_results)

    non_constituency_counts = df_non_constituency["Session Length Bins"].value_counts().sort_index()
    df_non_constituency_results = non_constituency_counts.reset_index()
    df_non_constituency_results.columns = ["Session Length", "Count"]
    df_non_constituency_results["Constituency"] = ["Outside"] * len(df_non_constituency_results)

    df_outcome = pd.concat([df_constituency_results, df_non_constituency_results], ignore_index=True)

    save_df_to_s3(df_outcome, mp_name, "month_conversations_by_length")


def make_df_chart_conversations_by_messages_bar(df, mp_name, constituency):
    df_constituency = df[df["Constituency"] == constituency]
    df_non_constituency = df[df["Constituency"] != constituency]

    bins = [1, 6, 11, 20, float("inf")]
    labels = [
        "1-5",
        "6-10",
        "11-19",
        "20+",
    ]

    df_constituency["Message Bins"] = pd.cut(df_constituency["Number of User Messages"], bins=bins, labels=labels, right=False, include_lowest=True)
    df_non_constituency["Message Bins"] = pd.cut(
        df_non_constituency["Number of User Messages"], bins=bins, labels=labels, right=False, include_lowest=True
    )

    constituency_counts = df_constituency["Message Bins"].value_counts().sort_index()
    df_constituency_results = constituency_counts.reset_index()
    df_constituency_results.columns = ["Message Count Category", "Count"]
    df_constituency_results["Constituency"] = ["Inside"] * len(df_constituency_results)

    non_constituency_counts = df_non_constituency["Message Bins"].value_counts().sort_index()
    df_non_constituency_results = non_constituency_counts.reset_index()
    df_non_constituency_results.columns = ["Message Count Category", "Count"]
    df_non_constituency_results["Constituency"] = ["Outside"] * len(df_non_constituency_results)

    df_outcome = pd.concat([df_constituency_results, df_non_constituency_results], ignore_index=True)

    save_df_to_s3(df_outcome, mp_name, "month_conversations_by_messages")


def _median_score_by_day(df, score_col, day_list, output_labels):
    n_scores = 0

    for v in df[score_col]:
        if len(v) > 0:
            n_scores = len(v[0])
            break

    if n_scores == 0:
        n_scores = len(output_labels)

    elif len(output_labels) != n_scores:
        raise ValueError("Length of output_labels does not match number of scores in arrays.")

    results = []
    for day in day_list:
        mask = (df["Session Date"] == day)
        medians = [0] * n_scores

        if mask.any():
            all_scores = []

            for scores_batch in df.loc[mask, score_col]:
                all_scores.extend(scores_batch)

            arr = np.array(all_scores)

            if arr.size:
                medians = [float(np.median(arr[:, i])) for i in range(n_scores)]

        row_sum = sum(medians)

        if row_sum > 0:
            medians = [m / row_sum for m in medians]

        row = {"Session Date": day}
        row.update({out_name: round(val, 3) for out_name, val in zip(output_labels, medians)})

        results.append(row)

    return pd.DataFrame(results)


def _language_score_by_metric_bar(df, constituency, score_col, output_labels):
    df["Session Date"] = pd.to_datetime(df["Session Date"]).dt.date

    current_month = datetime.now().month
    current_year = datetime.now().year

    num_days = monthrange(current_year, current_month)[1]
    all_days = pd.date_range(
        start=f"{current_year}-{current_month:02d}-01", periods=num_days
    ).date

    df_constituency = df[df["Constituency"] == constituency]
    df_non_constituency = df[df["Constituency"] != constituency]

    df_median_by_day_constituency = _median_score_by_day(
        df_constituency,
        score_col=score_col,
        day_list=all_days,
        output_labels=output_labels,
    )

    df_median_by_day_constituency["Constituency"] = ["Inside"] * len(df_median_by_day_constituency)


    df_median_by_day_non_constituency = _median_score_by_day(
        df_non_constituency,
        score_col=score_col,
        day_list=all_days,
        output_labels=output_labels,
    )

    df_median_by_day_non_constituency["Constituency"] = ["Outside"] * len(df_median_by_day_non_constituency)


    df_combined = pd.concat([df_median_by_day_constituency, df_median_by_day_non_constituency], ignore_index=True)

    return df_combined


def make_df_chart_median_sentiment_by_day_line(df, mp_name, constituency):
    df_metric_by_day = _language_score_by_metric_bar(df, constituency, "User Sentiment Scores", ["Positive", "Neutral", "Negative"])

    save_df_to_s3(df_metric_by_day, mp_name, "month_median_sentiment_by_day")


def make_df_chart_median_stance_by_day_line(df, mp_name, constituency):
    df_metric_by_day = _language_score_by_metric_bar(df, constituency, "User Stance Scores", ["Supportive", "Neutral", "Oppositional"])

    save_df_to_s3(df_metric_by_day, mp_name, "month_median_stance_by_day")


def make_df_chart_median_ideology_by_day_line(df, mp_name, constituency):
    df_metric_by_day = _language_score_by_metric_bar(df, constituency, "User Ideology Scores", ["Far-left", "Center-left", "Centrist", "Center-right", "Far-right"])

    save_df_to_s3(df_metric_by_day, mp_name, "month_median_ideology_by_day")


def _get_topics(df, messages_col, omit_list):
    documents = [item for subarray in df[messages_col].to_list() for item in subarray]
    omit_set = set(omit_list)

    kw_extractor = yake.KeywordExtractor(lan="en", n=3, top=5)

    doc_keywords = []
    for doc in documents:
        keywords = kw_extractor.extract_keywords(doc)
        filtered = [kw for kw, score in keywords if all(word not in omit_set for word in kw.lower().split())]
        doc_keywords.append(filtered)

    all_keywords = list(itertools.chain.from_iterable(doc_keywords))
    keyword_counts = Counter(all_keywords)
    main_topics = keyword_counts.most_common(5)

    df_topics = pd.DataFrame(main_topics, columns=["Top Keyword", "Count"])
    
    return df_topics


def _get_topics_per_constituency(df, mp_name, messages_col):
    df_all_weeks = pd.DataFrame()

    if df.empty:
        df_all_weeks = pd.DataFrame({
            "Top Keyword": ["No data available"] * 4,
            "Count": [1] * 4,
            "Week": [1, 2, 3, 4]
        })

    else:
        for week_number, df_week in df.groupby("Week"):
            mp_name_lower = mp_name.lower()
            mp_first_name = mp_name_lower.split(" ")[0]
            mp_last_name = mp_name_lower.split(" ")[1].lower()

            omit_keywords = [mp_name_lower, mp_first_name, mp_last_name, f"{mp_first_name}s", f"{mp_first_name}'s", f"{mp_last_name}s", f"{mp_last_name}'s", "mp", "member of parliament", "person"]
            df_week_topics = _get_topics(df_week, messages_col, omit_keywords)

            df_week_topics["Week"] = week_number

            df_all_weeks = pd.concat([df_all_weeks, df_week_topics], ignore_index=True)

        weeks = [1, 2, 3, 4]
        existing_weeks = set(df_all_weeks["Week"])
        missing_weeks = set(weeks) - existing_weeks

        no_data_row = {
            "Top Keyword": "No data available",
            "Count": 1,
            "Week": None
        }

        rows_to_add = []
        for week_num in sorted(missing_weeks):
            row = no_data_row.copy()
            row["Week"] = week_num
            rows_to_add.append(row)

        if rows_to_add:
            df_missing = pd.DataFrame(rows_to_add)
            df_all_weeks = pd.concat([df_all_weeks, df_missing], ignore_index=True)

        df_all_weeks = df_all_weeks.sort_values("Week").reset_index(drop=True)


    return df_all_weeks


def make_df_chart_top_keywords_by_week_bar(df, mp_name, constituency):
    df["Session Date"] = pd.to_datetime(df["Session Date"], errors="coerce")
    df["Week"] = ((df["Session Date"].dt.day - 1) // 7) + 1

    df_constituency = df[df["Constituency"] == constituency]
    df_non_constituency = df[df["Constituency"] != constituency]

    df_constituency_weeks = _get_topics_per_constituency(df_constituency, mp_name, "User Messages")
    df_non_constituency_weeks = _get_topics_per_constituency(df_non_constituency, mp_name, "User Messages")

    df_constituency_weeks["Constituency"] = "Inside"
    df_non_constituency_weeks["Constituency"] = "Outside"

    df_combined = pd.concat([df_constituency_weeks, df_non_constituency_weeks], ignore_index=True)

    save_df_to_s3(df_combined, mp_name, "month_top_keywords_by_week")


def make_df_chart_top_web_keywords_by_week_bar(df, mp_name, constituency):
    df["Week"] = ((df["Session Date"].dt.day - 1) // 7) + 1

    df_filtered = df[df["AI Websearch Messages"].apply(lambda x: x != [])].reset_index(drop=True)

    df_filtered["AI Websearch Messages"] = df_filtered["AI Websearch Messages"].apply(
        lambda x: [s[145:] for s in x] if isinstance(x, list) else x
    )

    df_constituency = df_filtered[df_filtered["Constituency"] == constituency]
    df_non_constituency = df_filtered[df_filtered["Constituency"] != constituency]


    df_constituency_weeks = _get_topics_per_constituency(df_constituency, mp_name, "AI Websearch Messages")
    df_non_constituency_weeks = _get_topics_per_constituency(df_non_constituency, mp_name, "AI Websearch Messages")

    df_constituency_weeks["Constituency"] = "Inside"
    df_non_constituency_weeks["Constituency"] = "Outside"

    df_combined = pd.concat([df_constituency_weeks, df_non_constituency_weeks], ignore_index=True)

    save_df_to_s3(df_combined, mp_name, "month_top_web_keywords_by_week")


def make_df_chart_sensitive_messages_by_day_line(df, mp_name, constituency):
    current_month = datetime.now().month
    current_year = datetime.now().year

    df_expanded = df.loc[df.index.repeat(df["Number of Sensitive Messages"])].copy()
    df_expanded = df_expanded[df_expanded["Number of Sensitive Messages"] > 0]

    df_sensitive_messages_by_day = _num_by_day(df_expanded, current_year, current_month, "Session Date", "Count")
    
    save_df_to_s3(df_sensitive_messages_by_day, mp_name, "month_sensitive_messages_by_day")


def make_df_chart_reported_responses_by_day_line(df, mp_name, constituency):
    current_month = datetime.now().month
    current_year = datetime.now().year

    df_responses_by_day = _num_by_day(df, current_year, current_month, "Report Date", "Response")

    save_df_to_s3(df_responses_by_day, mp_name, "month_reported_responses_by_day")


def make_df_chart_top_keywords_reports_by_week_bar(df, mp_name, constituency):
    df["Report Date"] = pd.to_datetime(df["Report Date"])
    df["Week"] = ((df["Report Date"].dt.day - 1) // 7) + 1
    df["Response"] = df["Response"].apply(lambda x: [x])

    df_topics = _get_topics_per_constituency(df, mp_name, "Response")

    save_df_to_s3(df_topics, mp_name, "month_top_keywords_reports_by_week")


def get_charts(df_conversations, df_reports, mp_name, constituency):
    make_df_chart_sessions_by_day_line(df_conversations, mp_name, constituency)
    make_df_chart_political_knowledge_by_ward_map(df_conversations, mp_name, constituency)
    make_df_chart_conversations_by_hour_bar(df_conversations, mp_name, constituency)
    make_df_chart_conversations_by_length_bar(df_conversations, mp_name, constituency)
    make_df_chart_conversations_by_messages_bar(df_conversations, mp_name, constituency)

    make_df_chart_median_sentiment_by_day_line(df_conversations, mp_name, constituency)
    make_df_chart_median_stance_by_day_line(df_conversations, mp_name, constituency)
    make_df_chart_median_ideology_by_day_line(df_conversations, mp_name, constituency)

    make_df_chart_top_keywords_by_week_bar(df_conversations, mp_name, constituency)
    make_df_chart_top_web_keywords_by_week_bar(df_conversations, mp_name, constituency)

    make_df_chart_sensitive_messages_by_day_line(df_conversations, mp_name, constituency)
    make_df_chart_reported_responses_by_day_line(df_reports, mp_name, constituency)
    make_df_chart_top_keywords_reports_by_week_bar(df_reports, mp_name, constituency)


def preprocess_df_conversations(df):
    df["conversation_datetime"] = pd.to_datetime(df["conversation_datetime"])
    df["Session Date"] = pd.to_datetime(df["Session Date"])
    df["Session Start Time"] = pd.to_timedelta(df["Session Start Time"])
    df["Session Length"] = pd.to_timedelta(df["Session Length"])

    list_columns = [
        "User Messages",
        "User Message Lengths",
        "AI FRE Scores",
        "User FRE Scores",
        "User Sentiment Scores",
        "User Stance Scores",
        "User Ideology Scores",
        "AI Websearch Messages"
    ]

    for col in list_columns:
        df[col] = df[col].apply(lambda x: x if isinstance(x, list) else ast.literal_eval(x) if isinstance(x, str) else [])


    df["Number of User Messages"] = pd.to_numeric(df["Number of User Messages"])
    df["Number of AI Messages"] = pd.to_numeric(df["Number of AI Messages"])
    df["Number of Sensitive Messages"] = pd.to_numeric(df["Number of Sensitive Messages"])
    df["Number of AI Websearches"] = pd.to_numeric(df["Number of AI Websearches"])

    df["User Competency Scores"] = df["User Competency Scores"].apply(ast.literal_eval)
    competencies = pd.json_normalize(df["User Competency Scores"])
    df = df.join(competencies, rsuffix="_score")

    current_date = pd.Timestamp.now()

    start_of_month = pd.Timestamp(year=current_date.year, month=current_date.month, day=1)
    end_of_month = pd.Timestamp(year=current_date.year, month=current_date.month + 1, day=1) - pd.Timedelta(days=1)

    df_month = df[(df["Session Date"] >= start_of_month) & (df["Session Date"] <= end_of_month)]


    return df, df_month


def preprocess_df_reports(df):
    df["message_reported_datetime"] = pd.to_datetime(df["message_reported_datetime"])
    df["Report Date"] = df["message_reported_datetime"].dt.date

    list_columns = [
        "Previous Messages",
        "Reported Tags",
    ]

    for col in list_columns:
        df[col] = df[col].apply(lambda x: x if isinstance(x, list) else ast.literal_eval(x) if isinstance(x, str) else [])

    current_date = pd.Timestamp.now()

    start_of_month = pd.Timestamp(year=current_date.year, month=current_date.month, day=1)
    end_of_month = pd.Timestamp(year=current_date.year, month=current_date.month + 1, day=1) - pd.Timedelta(days=1)

    df_month = df[(df["Report Date"] >= start_of_month.date()) & (df["Report Date"] <= end_of_month.date())]

    return df, df_month


def analysis():

    for mp_dict in MPS:
        mp_name = mp_dict["Name"]
        constituency = mp_dict["Constituency"]

        mp_conversation_records = boto_utils.dynamodb_batch_fetch_records(conversation_table, "mp_name", mp_name)
        mp_reported_responses = boto_utils.dynamodb_batch_fetch_records(reported_responses_table, "mp_name", mp_name)
        
        df_conversations = pd.DataFrame(mp_conversation_records)
        df_reports = pd.DataFrame(mp_reported_responses)

        # TODO: For now, simply do analysis of current month. Maybe if time offer prev 3 months.
        df_conversations_all, df_conversations_month = preprocess_df_conversations(df_conversations)
        df_reports_all, df_reports_month = preprocess_df_reports(df_reports)

        # NOTE: Temporary
        df_conversations_month = df_conversations_month[df_conversations_month["mp_name"] == mp_name]
        df_reports_month = df_reports_month[df_reports_month["mp_name"] == mp_name]


        get_charts(df_conversations_month, df_reports_month, mp_name, constituency)


analysis()