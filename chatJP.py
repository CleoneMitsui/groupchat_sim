import streamlit as st
# from streamlit_gsheets import GSheetsConnection
# import pandas as pd
from google.oauth2 import service_account
import gspread
from gspread.exceptions import WorksheetNotFound
from utils import generate_participant_id


# set page config
st.set_page_config(page_title="Chatroom Demo (Japanese)", page_icon="💬")

# --- QUERY PARAM RETRIEVAL ---
params = st.query_params
prolific_pid = params.get("PROLIFIC_PID", "testuser")

if prolific_pid == "testuser":
    st.session_state.participant_id = f"test_{generate_participant_id()}"
else:
    st.session_state.participant_id = prolific_pid


# extract plain string for writing to sheet
st.session_state.prolific_pid_str = st.session_state.participant_id


# initialise page tracker
if "page" not in st.session_state:
    st.session_state.page = "chat"

# helper to go to next page
def next_page(new_page):
    st.session_state.page = new_page
    st.rerun()

## for demo use - intro & nickname entry

# # intro page
# if st.session_state.page == "intro":

#     # warning for not to refresh
#     import streamlit.components.v1 as components

#     # warning banner
#     st.markdown(
#         "<p style='color:red; font-weight:bold;'>⚠️ Please stay connected. If your internet connection is interrupted, this study will reset and your progress will be lost. Avoid refreshing the page, switching networks, or closing the tab during the study.</p>",
#         unsafe_allow_html=True
#     )

#     # js to block F5 and Ctrl+R
#     components.html(
#         """
#         <script>
#         document.addEventListener("keydown", function (e) {
#             if ((e.key === "F5") || (e.ctrlKey && e.key === "r")) {
#                 e.preventDefault();
#                 alert("Please do not refresh the page. Doing so will restart the study and erase your answers.");
#             }
#         });
#         </script>
#         """,
#         height=0
#     )


     
#     st.markdown("<h2>Welcome to the Study</h2>", unsafe_allow_html=True)
#     # st.title("Welcome to the Study")
#     st.markdown("""
#      <div style='font-size:18px; line-height:1.6'>
                
#     You are being invited to participate in a research study conducted by Dr. Yuta Kawamura (Osaka Metropolitan University, Osaka, Japan). 
#                 If you have any questions or concerns about this study, feel free to contact the researchers via Prolific system.  

#     **Purpose of the Study:** This study explores how people interact in casual group conversations. 
    
#     **Procedures:** If you volunteer to participate in this study, you will complete a brief online interaction. 
#                 The process takes approximately 7~8 minutes to complete.  
    
#     **Requirements:** All participants must be Prolific participants, and be at least 18 years of age.
    
#     **Potential Risks and Discomforts:** You may get tired, but it should not exceed those experienced in everyday life.

#     **Potential Benefits to Participants and/or to Society:** You will receive no personal benefits for participating (other than compensation – see below). Your participation will contribute to ongoing academic research.

#     **Compensation for Participants:** For participating in this study, you will receive a base pay of £1.20.
    
#     **Confidentiality:** This study is conducted solely for academic research purposes. Therefore, the data collected from this study will be anonymised to ensure confidentiality, and no analysis will be performed that could lead to identification of individuals. While the raw data may be disclosed upon submission to academic journals, it will not be made public in a manner that could identify individuals. In the case that the data is not made public, the data will be retained by the researchers for up to 30 years before permanently deleted.

#     **Use of Generative AI:** In this study, you will be interacting with artificial intelligence (AI) agents in a simulated group chat. The text you enter during the chat will be processed by Generative AI models to produce responses in real time. In addition, your input may later be analysed using Generative AI tools for research purposes. Only the text you write during the experiment will be entered into the AI system. No personally identifiable information, such as your Prolific ID, will be included. Your input will be used to help improve our understanding of group communication. By continuing, you consent to both interacting with AI agents and having your written responses analysed using Generative AI.
                
#     **Participation and Withdrawal:** Participation in this study is not obligatory. Participants have the right to withdraw from the study at any point. Should you decide to discontinue the participation, you may do so by closing the browser. Data that is partially completed will be temporarily saved online but will be promptly discarded and not be subjected to analysis.

#     **Rights of Research Participants:** This project has been reviewed by the Osaka Metropolitan University Research Ethics Board for research involving human participants.
           
#     If you choose to continue to the study, the experimenter will assume that you consent to participate in this research.

#     Note: Please note that you can print a copy of this consent form for your records.

#     If you agree to participate, click below to begin. <br>
#     """,
#         unsafe_allow_html=True
#     )

#     if st.button("I Agree – continue"):
#         next_page("demographics")

# # demographics page
# elif st.session_state.page == "demographics":
#     import streamlit.components.v1 as components

#     # warning message
#     st.markdown(
#         "<p style='color:red; font-weight:bold;'>⚠️ Please do not refresh the page. Doing so will restart the study and erase your answers.</p>",
#         unsafe_allow_html=True
#     )

#     # block F5 / Ctrl+R
#     components.html(
#         """
#         <script>
#         document.addEventListener("keydown", function (e) {
#             if ((e.key === "F5") || (e.ctrlKey && e.key === "r")) {
#                 e.preventDefault();
#                 alert("Please do not refresh the page. Doing so will restart the study and erase your answers.");
#             }
#         });
#         </script>
#         """,
#         height=0
#     )

#     st.title("About You")
#     with st.form("demo_form"):
#         pid = st.query_params.get("PROLIFIC_PID", ["unknown"])
        
#         age_options = ["Choose an option"] + list(range(18, 80))
#         gender_options = ["Choose an option", "Male", "Female", "Other"]
#         ethnicity_options = ["Choose an option",
#                             "American Indian or Alaska Native",
#                             "Asian or Asian American",
#                             "Black or African American",
#                             "Hispanic or Latino",
#                             "Middle Eastern or North African",
#                             "Native Hawaiian or other Pacific Islander",
#                             "White",
#                             "Other"]
#         education_options = [
#             "Choose an option",
#             "Less than high school", "High school graduate", "Some college, no degree",
#             "Associate degree (e.g., AA, AS)", "Bachelor's degree (e.g., BA, BS)",
#             "Master's degree (e.g., MA, MS, MEd)", "Professional degree (e.g., MD, JD)",
#             "Doctorate (e.g., PhD, EdD)"
#         ]

#         age = st.selectbox("Please provide your age.", age_options, index=0)
#         gender = st.selectbox("Please indicate your gender.", gender_options, index=0)
#         ethnicity = st.selectbox("Which of the following category best describes you?", ethnicity_options, index=0)
#         education = st.selectbox("What is the highest level of education you have completed?", education_options, index=0)

#         submitted = st.form_submit_button("Next")

#         if submitted and all(x != "Choose an option" for x in [gender, ethnicity, education, age]):
#             st.session_state.demographics = {
#                 "prolific_id": pid,
#                 "age": age,
#                 "gender": gender,
#                 "ethnicity": ethnicity,
#                 "education": education,
#             }
#             next_page("chat")
#         elif submitted:
#             st.warning("Please answer all questions before continuing.")


# =========== CHAT ===========
if st.session_state.page == "chat":
    import chatroom
    chatroom.render_chat() 

# =========== POST CHAT PAGE ===========
elif st.session_state.page == "post":
    st.markdown("Loading final questions...")
    import time
    time.sleep(0.5)
    next_page("final_survey")

# =========== FINAL SURVEY ===========
elif st.session_state.page == "final_survey":

    st.header("Final Questions")

    st.markdown('<p class="big-label">チャット中にどの程度このように感じたかをお答えください。</p>', unsafe_allow_html=True)
    emotion_labels = ["興味を感じた", "楽しかった", "わくわくした", "いらいらした", "怒りを感じた"]
    emotion_options = [
        "1 - 全く感じなかった",
        "2 - 少し感じた",
        "3 - まあまあ感じた",
        "4 - かなり感じた",
        "5 - 非常に強く感じた"
    ]
    emotion_responses = {}

    # resize fonts for emotion headings and radio options + text area
    st.markdown("""
    <style>
    .radio-label {
        font-size: 18px !important;
        line-height: 1.6 !important;
        font-weight: 500;
        margin-top: 0rem;
    }
    .radio-label + .radio-label {
        margin-top: 0.2rem;
    }

    textarea {
        font-size: 18px !important;
        line-height: 1.6 !important;
    }

    .big-label {
        font-size: 18px !important;
        line-height: 1.6 !important;
        font-weight: 500;
        margin-bottom: 0.2rem !important;  
    }
    </style>
    """, unsafe_allow_html=True)


    for label in emotion_labels:
        st.markdown(f"<div class='radio-label'>{label}</div>", unsafe_allow_html=True)
        response = st.radio(
            label=label,
            options=emotion_options,
            index=None,
            key=f"radio_{label}",
            label_visibility="collapsed"
        )
        emotion_responses[label] = response


    st.markdown(" ")
    st.markdown('<p class="big-label">何か感想や気づいたことがあれば自由にご記入ください。</p>', unsafe_allow_html=True)
    comment = st.text_area(
        label="何か感想や気づいたことがあれば自由にご記入ください。",
        label_visibility="collapsed",
        height=200
    )



    # --- value mappings ---
    GENDER_MAP = {"Male": 1, "Female": 2, "Other": 3}
    ETHNICITY_MAP = {
        "American Indian or Alaska Native": 1, "Asian or Asian American": 2,
        "Black or African American": 3, "Hispanic or Latino": 4,
        "Middle Eastern or North African": 5,
        "Native Hawaiian or other Pacific Islander": 6, "White": 7, "Other": 8
    }
    EDUCATION_MAP = {
        "Less than high school": 1, "High school graduate": 2,
        "Some college, no degree": 3, "Associate degree (e.g., AA, AS)": 4,
        "Bachelor's degree (e.g., BA, BS)": 5, "Master's degree (e.g., MA, MS, MEd)": 6,
        "Professional degree (e.g., MD, JD)": 7, "Doctorate (e.g., PhD, EdD)": 8
    }
    IDEOLOGY_MAP = {"liberal": 1, "conservative": 2}
    TOPIC_MAP = {"guns": 1, "immigration": 2, "abortion": 3, "vaccines": 4, "gender": 5}

    if st.button("Submit"):
        # validation: make sure emotional questions are answered
        if any(v is None for v in emotion_responses.values()):
            st.warning("Please answer all the emotional experience questions.")
            st.stop()

        # store responses in session
        st.session_state.comment = comment
        st.session_state.emotion_responses = emotion_responses

        agent_names = st.session_state.group_members
        trait_dict = st.session_state.trait_dict
        avatar_map = st.session_state.avatar_map

        agent_big5 = ", ".join([trait_dict[name] for name in agent_names])
        agent_avatar = ", ".join([avatar_map[name].split(".")[0][-2:] for name in agent_names])

        # demographics may be missing in demo; fill blanks gracefully
        demo = st.session_state.get("demographics", {})
        age = demo.get("age", "")
        gender = GENDER_MAP.get(demo.get("gender", ""), "")
        ethnicity = ETHNICITY_MAP.get(demo.get("ethnicity", ""), "")
        education = EDUCATION_MAP.get(demo.get("education", ""), "")


        try:
            credentials = service_account.Credentials.from_service_account_info(
                st.secrets["connections"]["gsheets"],
                scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
            gc = gspread.authorize(credentials)
            sheet = gc.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])

            try:
                worksheet = sheet.worksheet("JP_Demo")
            except WorksheetNotFound:
                worksheet = sheet.add_worksheet("JP_Demo", rows=1000, cols=26)

                worksheet.append_row([
                    "PROLIFIC_PID", "age", "sex", "ethnicity", "education",
                    "agent_big5", "agent_avatar",
                    "condition", "topic",
                    "response1",
                    "agent_round2", "response2",
                    "agent_round3", "response3",
                    "agent_round4", "response4",
                    "agent_round5", "response5",
                    "reaction_time1", "reaction_time2", "reaction_time3", "reaction_time4", "reaction_time5",
                    "comment",
                    "interested", "happy", "excited", "irritable", "angry"
                ])

            # row building
            row = [
                st.session_state.prolific_pid_str,
                age, gender, ethnicity, education,   # use the safe fallbacks
                agent_big5,
                agent_avatar,
                IDEOLOGY_MAP.get(st.session_state.group_ideology, ""),
                TOPIC_MAP.get(st.session_state.selected_topic, ""),
            ]


            user_responses = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
            agent_rounds = st.session_state.get("agent_rounds_raw", [])
            reaction_times = st.session_state.get("reaction_times", [])

            while len(user_responses) < 5:
                user_responses.append("")
            while len(agent_rounds) < 4:
                agent_rounds.append("")
            while len(reaction_times) < 5:
                reaction_times.append("")

            row.append(user_responses[0])  # response1
            for i in range(4):
                row.append(agent_rounds[i])
                row.append(user_responses[i + 1])
            for rt in reaction_times[:5]:
                row.append(rt)

            row.append(st.session_state.comment)

            for emotion in emotion_labels:
                response = st.session_state.emotion_responses.get(emotion, "")
                if response:
                    row.append(int(response[0]))  # get the number before " - ..."
                else:
                    row.append("")


            worksheet.append_row(row, value_input_option="USER_ENTERED")

        except Exception as e:
            st.error(f"Google Sheet recording failed: {e}")
            st.stop()

        next_page("thankyou")



# end page
elif st.session_state.page == "thankyou":
    st.markdown("<h2>ご協力ありがとうございます！</h2>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="font-size:18px; line-height:1.8;">
        Your responses have been recorded.<br>

        <strong>Debriefing</strong><br>
        Please note that <b>all dialogue was generated by artificial intelligence (AI)</b>.
        These responses were carefully designed and pre-tested by the research team to ensure they aligned with the intended experimental conditions and met ethical standards for participant welfare.
        Since the content was generated live during the study, fact-checking was not possible in real time. The political views expressed within the chat do not reflect the personal beliefs of the researchers. They were used solely to serve the purposes of the study. 
        We apologise for any discomfort caused, and we thank you for your understanding and participation.<br>

        本研究に関してご質問がある場合は、<br>三井クリオネ (Cleone Mitsui) までご連絡ください。<br>
        メールアドレス: sa24779n[at]st.omu.ac.jp
        </div>
        """,
        unsafe_allow_html=True
    )
