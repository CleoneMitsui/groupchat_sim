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
                
    If you have any questions or concerns about this study, feel free to contact the researchers via Prolific system.

    **Purpose of the Study:** This study explores how people interact in casual group conversations. 
    
    **Procedures:** If you volunteer to participate in this study, you will complete a brief online interaction. 
                The process takes approximately 5 minutes to complete.
    
    **Requirements:** All participants must be Prolific participants, and be at least 18 years of age.
    
    **Potential Risks and Discomforts:** You may get tired, but it should not exceed those experienced in everyday life.

    **Potential Benefits to Participants and/or to Society:** You will receive no personal benefits for participating (other than compensation – see below). Your participation will contribute to ongoing academic research.

    **Compensation for Participants:** For participating in this study, you will receive a base pay of £X.XX.
    
    **Confidentiality:** This study is conducted solely for academic research purposes. Therefore, the data collected from this study will be anonymised to ensure confidentiality, and no analysis will be performed that could lead to identification of individuals. While the raw data may be disclosed upon submission to academic journals, it will not be made public in a manner that could identify individuals. In the case that the data is not made public, the data will be retained by the researchers for up to 30 years before permanently deleted.

    **Participation and Withdrawal:** Participation in this study is not obligatory. Participants have the right to withdraw from the study at any point. Should you decide to discontinue the participation, you may do so by closing the browser. Data that is partially completed will be temporarily saved online but will be promptly discarded and not be subjected to analysis.

    **Rights of Research Participants:** This project has been reviewed by the XXX Research Ethics Board for research involving human participants.

    If you choose to continue to the study, the experimenter will assume that you consent to participate in this research.

    Note: Please note that you can print a copy of this consent form for your records.

    If you agree to participate, click below to begin.
    """)
    if st.button("I Agree – continue"):
        next_page("demographics")

# demographics page
elif st.session_state.page == "demographics":
    st.title("About You")
    with st.form("demo_form"):
        pid = st.query_params.get("PROLIFIC_PID", ["unknown"])[0]
        
        age_options = ["Choose an option"] + list(range(18, 80))
        gender_options = ["Choose an option", "Male", "Female", "Other"]
        ethnicity_options = ["Choose an option", "White", "Black", "Asian", "Native American", "Hispanic", "Other"]
        education_options = [
            "Choose an option",
            "Less than high school", "High school graduate", "Some college, no degree",
            "Associate degree (e.g., AA, AS)", "Bachelor's degree (e.g., BA, BS)",
            "Master's degree (e.g., MA, MS, MEd)", "Professional degree (e.g., MD, JD)",
            "Doctorate (e.g., PhD, EdD)"
        ]

        age = st.selectbox("Please provide your age.", age_options, index=0)
        gender = st.selectbox("Please indicate your gender.", gender_options, index=0)
        ethnicity = st.selectbox("Which of the following category best describes you?", ethnicity_options, index=0)
        education = st.selectbox("What is the highest level of education you have completed?", education_options, index=0)

        submitted = st.form_submit_button("Next")

        if submitted and all(x != "Choose an option" for x in [gender, ethnicity, education, age]):
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
    # st.subheader("That is the end of the study.")
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