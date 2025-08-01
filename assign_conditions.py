import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

def get_even_assignment(participant_id, secret_dict):
    creds = Credentials.from_service_account_info(
        secret_dict,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_url(secret_dict["spreadsheet"])
    worksheet = sheet.worksheet("Assignment")

    data = worksheet.get_all_values()
    if len(data) <= 1:
        df = pd.DataFrame(columns=["participant_id", "assigned_ideology", "assigned_topic"])
    else:
        df = pd.DataFrame(data[1:], columns=data[0])

    # --- duplicate protection ---
    existing = df[df["participant_id"] == participant_id]
    if not existing.empty:
        row = existing.iloc[0]
        return row["assigned_ideology"], row["assigned_topic"]

    # --- setup ---
    all_topics = ["guns", "immigration", "abortion", "vaccines", "gender"]

    # count how many times each ideology has been assigned
    ideology_counts = df["assigned_ideology"].value_counts().to_dict()

    # count how many times each topic has been assigned within each ideology
    # create stratified counts table with all combinations
    index = ["liberal", "conservative"]
    columns = all_topics
    stratified_counts = pd.DataFrame(0, index=index, columns=columns)

    if not df.empty:
        current_counts = df.groupby(["assigned_ideology", "assigned_topic"]).size()
        for (ideol, topic), count in current_counts.items():
            stratified_counts.loc[ideol, topic] = count


    # --- assign ideology with fewer total assigned so far ---
    liberal_count = ideology_counts.get("liberal", 0)
    conservative_count = ideology_counts.get("conservative", 0)
    ideology = "liberal" if liberal_count <= conservative_count else "conservative"

    # --- assign topic with lowest count for the selected ideology ---
    topic = stratified_counts.loc[ideology].idxmin()

    # --- write to sheet ---
    worksheet.append_row([
        participant_id,
        ideology,
        topic
    ], value_input_option="USER_ENTERED")

    return ideology, topic
