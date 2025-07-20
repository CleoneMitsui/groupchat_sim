import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

def get_even_assignment(participant_id, nickname, secret_dict):
    creds = Credentials.from_service_account_info(
        secret_dict,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_url(secret_dict["spreadsheet"])
    worksheet = sheet.worksheet("Assignment")

    data = worksheet.get_all_values()
    if len(data) <= 1:
        df = pd.DataFrame(columns=["participant_id", "nickname", "assigned_ideology", "assigned_topic"])
    else:
        df = pd.DataFrame(data[1:], columns=data[0])

    # duplicate protection
    existing = df[df["participant_id"] == participant_id]
    if not existing.empty:
        row = existing.iloc[0]
        return row["assigned_ideology"], row["assigned_topic"]

    # assign new
    ideology_counts = df["assigned_ideology"].value_counts().to_dict()
    topic_counts = df["assigned_topic"].value_counts().to_dict()
    all_topics = ["guns", "immigration", "abortion", "vaccines", "gender"]

    ideology = "liberal" if ideology_counts.get("liberal", 0) <= ideology_counts.get("conservative", 0) else "conservative"
    topic = min(all_topics, key=lambda t: topic_counts.get(t, 0))

    worksheet.append_row([
        participant_id,
        nickname,
        ideology,
        topic
    ], value_input_option="USER_ENTERED")

    return ideology, topic

