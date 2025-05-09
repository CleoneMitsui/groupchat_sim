import streamlit as st
# from streamlit_gsheets import GSheetsConnection
import pandas as pd
from google.oauth2 import service_account
import gspread
from gspread.exceptions import WorksheetNotFound

# set page config
st.set_page_config(page_title="Chatroom Study", page_icon="💬")

# initialise page tracker
if "page" not in st.session_state:
    st.session_state.page = "intro"

# connect to google sheets
# conn = st.connection("gsheets", type=GSheetsConnection)

# helper to go to next page
def next_page(new_page):
    st.session_state.page = new_page
    st.rerun()

# intro page
if st.session_state.page == "intro":
    st.title("Welcome to the Study")
    st.markdown("""
    You are being invited to participate in a research study conducted by ...

    This study explores how people interact in casual group conversations. The study will take approximately 5 minutes.

    Your responses will remain anonymous, and all data will be stored securely.

    If you agree to participate, click below to begin.
    """)
    if st.button("I Agree – continue"):
        next_page("demographics")

# demographics page
elif st.session_state.page == "demographics":
    st.title("About You")
    with st.form("demo_form"):
        pid = st.query_params.get("PROLIFIC_PID", ["unknown"])[0]
        age = st.selectbox("Your age", list(range(18, 80)))
        gender = st.radio("Gender", ["Male", "Female", "Other"], index=None)
        ethnicity = st.selectbox("Ethnicity", ["White", "Black", "Asian", "Native American", "Hispanic", "Other"], index=None)
        education = st.selectbox("Highest education level", [
            "Less than high school", "High school graduate", "Some college, no degree",
            "Associate degree (e.g., AA, AS)", "Bachelor's degree (e.g., BA, BS)", "Master's degree (e.g., MA, MS, MEd)", "Professional degree (e.g., MD, JD)", "Doctorate (e.g., PhD, EdD)"], index=None)
        submitted = st.form_submit_button("Next")
        if submitted and gender and ethnicity and education:
            st.session_state.demographics = {
                "prolific_id": pid,
                "age": age,
                "gender": gender,
                "ethnicity": ethnicity,
                "education": education,
            }
            next_page("chat")
        elif submitted:
            st.warning("Please answer all questions before continuing.")

# chatroom page 
elif st.session_state.page == "chat":
    import chatroom
    chatroom.render_chat() 

# post-survey page
elif st.session_state.page == "post":
    # value mappings
    GENDER_MAP = {"Male": 1, "Female": 2, "Other": 3}
    ETHNICITY_MAP = {"White": 1, "Black": 2, "Asian": 3, 
                    "Native American": 4, "Hispanic": 5, "Other": 6}
    EDUCATION_MAP = {
        "Less than high school": 1,
        "High school graduate": 2,
        "Some college, no degree": 3,
        "Associate degree (e.g., AA, AS)": 4,
        "Bachelor's degree (e.g., BA, BS)": 5,
        "Master's degree (e.g., MA, MS, MEd)": 6,
        "Professional degree (e.g., MD, JD)": 7,
        "Doctorate (e.g., PhD, EdD)": 8
    }

    try:
        # Create credentials from Streamlit secrets
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["connections"]["gsheets"],
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        gc = gspread.authorize(credentials)
        sheet = gc.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        
        # Get or create worksheet
        try:
            worksheet = sheet.worksheet("StudyData")
        except WorksheetNotFound:
            worksheet = sheet.add_worksheet("StudyData", rows=1000, cols=8)
            worksheet.append_row([
                "PID", "Age", "Sex", "Ethnicity", "Education",
                "Speaker", "Content", "Timestamp"
            ])

        # prepare data
        base_data = [
            st.session_state.demographics["prolific_id"],
            st.session_state.demographics["age"],
            GENDER_MAP[st.session_state.demographics["gender"]],
            ETHNICITY_MAP[st.session_state.demographics["ethnicity"]],
            EDUCATION_MAP[st.session_state.demographics["education"]]
        ]

   
        # Append all messages using gspread
        for msg in st.session_state.messages:
            row = base_data + [
                1 if msg["role"] == "user" else 0,  # Speaker code
                msg["content"],
                msg["timestamp"]
            ]
            worksheet.append_row(row)

    except Exception as e:
        st.error(f"Error saving data: {str(e)}")
    
    next_page("thankyou")

# end page
elif st.session_state.page == "thankyou":
    st.title("Thank you for your participation!")
    st.markdown("""
    Your responses have been recorded.

    If you have any questions about this study, please contact us through Prolific.
    """)
    PROLIFIC_COMPLETION_URL = "https://app.prolific.com/submissions/complete?cc=CJQL982C"
    st.markdown(
        f"<p style='text-align:center'><a href='{PROLIFIC_COMPLETION_URL}' target='_blank'>"
        f"<button style='font-size:18px;'>Click here to complete the study on Prolific</button></a></p>",
        unsafe_allow_html=True
    )