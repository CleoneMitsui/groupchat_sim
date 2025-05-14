import streamlit as st
# from streamlit_gsheets import GSheetsConnection
import pandas as pd
from google.oauth2 import service_account
import gspread
from gspread.exceptions import WorksheetNotFound

# force thank you end page for content checking
# st.session_state.page = "thankyou"


# set page config
st.set_page_config(page_title="Chatroom Study", page_icon="💬")

# read URL query parameters (PROLIFIC_PID, STUDY_ID, SESSION_ID)
params = st.query_params
st.session_state.prolific_pid = params.get("PROLIFIC_PID", ["unknown"])[0]
st.session_state.study_id = params.get("STUDY_ID", ["unknown"])[0]
st.session_state.session_id = params.get("SESSION_ID", ["unknown"])[0]

# for debugging display
# st.write("Captured PID:", st.session_state.prolific_pid)
# st.write("Captured STUDY_ID:", st.session_state.study_id)
# st.write("Captured SESSION_ID:", st.session_state.session_id)



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
    st.markdown("<h2>Welcome to the Study</h2>", unsafe_allow_html=True)
    # st.title("Welcome to the Study")
    st.markdown("""
     <div style='font-size:18px; line-height:1.6'>
                
    You are being invited to participate in a research study conducted by [anonymised for the app-building period]. 
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

    If you agree to participate, click below to begin. <br>
    """,
        unsafe_allow_html=True
    )

    if st.button("I Agree – continue"):
        next_page("demographics")

# demographics page
elif st.session_state.page == "demographics":
    st.title("About You")
    with st.form("demo_form"):
        pid = st.query_params.get("PROLIFIC_PID", ["unknown"])[0]
        
        age_options = ["Choose an option"] + list(range(18, 80))
        gender_options = ["Choose an option", "Male", "Female", "Other"]
        ethnicity_options = ["Choose an option",
                            "American Indian or Alaska Native",
                            "Asian or Asian American",
                            "Black or African American",
                            "Hispanic or Latino",
                            "Middle Eastern or North African",
                            "Native Hawaiian or other Pacific Islander",
                            "White",
                            "Other"]
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
    ETHNICITY_MAP = {"American Indian or Alaska Native": 1,
                    "Asian or Asian American": 2,
                    "Black or African American": 3,
                    "Hispanic or Latino": 4,
                    "Middle Eastern or North African": 5,
                    "Native Hawaiian or other Pacific Islander": 6,
                    "White": 7,
                    "Other": 8}
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
    IDEOLOGY_MAP = {"liberal": 1, "conservative": 2}
    TOPIC_MAP = {
        "guns": 1, "immigration": 2, "abortion": 3,
        "vaccines": 4, "gender": 5
    }


    try:
        # create credentials from streamlit secrets
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["connections"]["gsheets"],
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        gc = gspread.authorize(credentials)
        sheet = gc.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        
        # get worksheet
        try:
            worksheet = sheet.worksheet("StudyData")
        except WorksheetNotFound:
            worksheet = sheet.add_worksheet("StudyData", rows=1000, cols=8)
            worksheet.append_row([
                "PROLIFIC_PID", "age", "sex", "ethnicity", "education",
                "condition", "topic", "response1", "response2", "response3"
            ])
        
        # collect 3 participant inputs
        user_messages = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
        response1 = user_messages[0] if len(user_messages) > 0 else ""
        response2 = user_messages[1] if len(user_messages) > 1 else ""
        response3 = user_messages[2] if len(user_messages) > 2 else ""

        row = [
            st.session_state.prolific_pid,
            st.session_state.demographics["age"],
            GENDER_MAP[st.session_state.demographics["gender"]],
            ETHNICITY_MAP[st.session_state.demographics["ethnicity"]],
            EDUCATION_MAP[st.session_state.demographics["education"]],
            IDEOLOGY_MAP[st.session_state.group_ideology],
            TOPIC_MAP[st.session_state.selected_topic],
            response1,
            response2,
            response3
        ]
        worksheet.append_row(row)

    except Exception as e:
        st.error(f"Error saving data: {str(e)}")
    
    next_page("thankyou")

# end page
elif st.session_state.page == "thankyou":
    st.markdown("<h2>Thank you for your participation!</h2>", unsafe_allow_html=True)
    # st.title("Thank you for your participation!") 
    # st.subheader("That is the end of the study.")
    st.markdown("""
    
     <div style='font-size:18px; line-height:1.6'>
    <br>Your responses have been recorded.    

    <br><strong>Debriefing</strong><br>

    Please note that while the group chat interface may have appeared to be a live conversation, <b>all dialogue was generated by artificial intelligence (AI)</b>.
                 These responses were carefully designed and pre-tested by the research team to ensure they aligned with the intended experimental conditions and 
                met ethical standards for participant welfare. 

    The political views expressed within the chat do not reflect the personal beliefs of the researchers. They were used solely to serve the purposes of the study.
                We apologise for any discomfort caused, and we thank you for your understanding and participation. 
                If you have any questions about this study, please contact us through Prolific.
                </div><br>
    """,
        unsafe_allow_html=True
    )

    PROLIFIC_COMPLETION_URL = "https://app.prolific.com/submissions/complete?cc=CJQL982C"
    st.markdown(
        f"""
        <style>
        .important-button {{
            background-color: #28a745;  /* bright green */
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 18px;
            border-radius: 8px;
            cursor: pointer;
        }}
        .important-button:hover {{
            background-color: #218838;  /* darker green on hover */
        }}
        </style>

        <p style='text-align:center'>
            <a href='{PROLIFIC_COMPLETION_URL}' target='_blank'>
                <button class='important-button'>Click here to complete the study on Prolific</button>
            </a>
        </p>
        """,
        unsafe_allow_html=True
    )
